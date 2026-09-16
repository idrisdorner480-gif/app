import hashlib
import re
from datetime import datetime, timedelta, timezone
from typing import Any

import httpx

from lib.db import db
from models.products import Product, StoreOffer

OPEN_FACTS_CATALOGS = {
    "Open Food Facts": "https://world.openfoodfacts.org",
    "Open Products Facts": "https://world.openproductsfacts.org",
    "Open Beauty Facts": "https://world.openbeautyfacts.org",
}
OFF_FIELDS = ",".join(
    [
        "code",
        "product_name",
        "product_name_de",
        "brands",
        "quantity",
        "categories",
        "categories_tags",
        "image_front_url",
        "image_url",
    ]
)
OFF_USER_AGENT = "MarktFuchs/1.0 (public product comparison demo)"
CACHE_TTL_HOURS = 12
FALLBACK_IMAGE = "https://images.unsplash.com/photo-1542838132-92c53300491e?auto=format&fit=crop&w=900&q=80"

CITY_ADDRESS_BASES = {
    "Berlin": ("Alexanderplatz", "10178"),
    "Hamburg": ("Mönckebergstraße", "20095"),
    "Munich": ("Kaufingerstraße", "80331"),
    "München": ("Kaufingerstraße", "80331"),
    "Köln": ("Schildergasse", "50667"),
    "Vienna": ("Mariahilfer Straße", "1070"),
    "Wien": ("Mariahilfer Straße", "1070"),
    "Graz": ("Herrengasse", "8010"),
    "Linz": ("Landstraße", "4020"),
    "Salzburg": ("Linzer Gasse", "5020"),
    "Innsbruck": ("Museumstraße", "6020"),
}


def stable_number(value: str) -> int:
    return int(hashlib.sha256(value.encode("utf-8")).hexdigest()[:10], 16)


def safe_slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def branch_details(store: str, country_code: str, city: str, index: int) -> tuple[str, str, str]:
    street, postal_code = CITY_ADDRESS_BASES.get(city, ("Zentrumstraße", "00000"))
    number = 3 + ((stable_number(f"{store}-{city}") + index) % 47)
    branch_id = f"{country_code.lower()}-{safe_slug(city)}-{safe_slug(store)}-{index + 1}"
    branch_name = f"{store} {city} · Demo-Filiale"
    address = f"{street} {number}, {postal_code} {city} · Demo-Adresse"
    return branch_id, branch_name, address


def quantity_divisor(quantity: str) -> float:
    normalized = quantity.lower().replace(",", ".")
    match = re.search(r"(\d+(?:\.\d+)?)\s*(kg|g|l|ml)", normalized)
    if not match:
        pieces = re.search(r"(\d+)\s*x", normalized)
        return float(pieces.group(1)) if pieces else 1.0
    amount = float(match.group(1))
    unit = match.group(2)
    if unit in {"g", "ml"}:
        return max(amount / 1000, 0.01)
    return max(amount, 0.01)


def demo_branch_offers(
    product_key: str,
    quantity: str,
    country_code: str,
    city: str,
    stores: list[str],
) -> list[StoreOffer]:
    divisor = quantity_divisor(quantity)
    offers: list[StoreOffer] = []
    for index, store in enumerate(stores):
        seed = stable_number(f"{product_key}-{country_code}-{city}-{store}")
        status = "verfügbar" if index == 0 else ["verfügbar", "verfügbar", "knapp", "nicht verfügbar"][seed % 4]
        price = round(0.89 + (seed % 2200) / 100, 2)
        branch_id, branch_name, address = branch_details(store, country_code, city, index)
        offers.append(
            StoreOffer(
                store=store,
                country_code=country_code,
                branch_id=branch_id,
                branch_name=branch_name,
                address=address,
                price=price,
                unit_price=round(price / divisor, 2),
                distance_km=round(0.4 + (seed % 45) / 10, 1),
                available=status != "nicht verfügbar",
                stock_status=status,
                discount_percent=10 + seed % 16 if seed % 5 == 0 else 0,
            )
        )
    return offers


def attach_branch_to_offer(offer: StoreOffer, city: str, index: int) -> StoreOffer:
    branch_id, branch_name, address = branch_details(offer.store, offer.country_code, city, index)
    return offer.model_copy(
        update={
            "branch_id": branch_id,
            "branch_name": branch_name,
            "address": address,
            "stock_status": "verfügbar" if offer.available else "nicht verfügbar",
        }
    )


def category_label(raw: dict[str, Any]) -> str:
    categories = raw.get("categories")
    if isinstance(categories, str) and categories.strip():
        return categories.split(",")[0].strip()
    tags = raw.get("categories_tags") or []
    if tags:
        return str(tags[0]).split(":")[-1].replace("-", " ").title()
    return "Lebensmittel"


def map_off_product(
    raw: dict[str, Any],
    query: str,
    country_code: str,
    city: str,
    stores: list[str],
    catalog_name: str,
    catalog_base: str,
) -> Product | None:
    code = str(raw.get("code") or "").strip()
    name = str(raw.get("product_name_de") or raw.get("product_name") or "").strip()
    if not code or not name:
        return None
    brand = str(raw.get("brands") or "Unbekannte Marke").split(",")[0].strip()
    quantity = str(raw.get("quantity") or "Packung").strip()
    image_url = str(raw.get("image_front_url") or raw.get("image_url") or FALLBACK_IMAGE)
    category = category_label(raw)
    return Product(
        id=f"off-{code}",
        barcode=code,
        name=name,
        brand=brand,
        category=category,
        package_size=quantity,
        image_url=image_url,
        data_source=catalog_name,
        product_url=f"{catalog_base}/product/{code}",
        keywords=[query, brand, category],
        offers=demo_branch_offers(code, quantity, country_code, city, stores),
    )


async def search_open_food_products(
    query: str,
    country_code: str,
    city: str,
    stores: list[str],
    page: int,
    page_size: int,
) -> tuple[list[Product], int, str]:
    if country_code not in {"DE", "AT"} or len(query.strip()) < 2 or not stores:
        return [], 0, "MarktFuchs Demo-Katalog"

    normalized_query = query.casefold().strip()
    beauty_terms = {"drogerie", "shampoo", "duschgel", "seife", "zahnpasta", "kosmetik", "deo", "creme"}
    household_terms = {"haushalt", "waschmittel", "reiniger", "spülmittel", "toilettenpapier", "küchenrolle"}
    if any(term in normalized_query for term in beauty_terms):
        catalog_names = ["Open Beauty Facts", "Open Products Facts", "Open Food Facts"]
    elif any(term in normalized_query for term in household_terms):
        catalog_names = ["Open Products Facts", "Open Food Facts"]
    else:
        catalog_names = ["Open Food Facts"]

    key = f"open-facts-v2:{country_code}:{normalized_query}:{page}:{page_size}:{'-'.join(catalog_names)}"
    now = datetime.now(timezone.utc)
    cached = await db.catalog_cache.find_one({"key": key, "expires_at": {"$gt": now}})
    payload: dict[str, Any] | None = cached.get("payload") if cached else None
    source = "Open Food Facts · Cache" if payload else "Open Food Facts"

    if payload is None:
        combined_products: list[dict[str, Any]] = []
        combined_count = 0
        successful_catalogs: list[str] = []
        async with httpx.AsyncClient(
            timeout=httpx.Timeout(9.0, connect=3.0),
            headers={"User-Agent": OFF_USER_AGENT, "Accept": "application/json"},
            follow_redirects=True,
        ) as client:
            for catalog_name in catalog_names:
                catalog_base = OPEN_FACTS_CATALOGS[catalog_name]
                params = {
                    "search_terms": query,
                    "search_simple": "1",
                    "action": "process",
                    "json": "1",
                    "page": str(page),
                    "page_size": str(page_size),
                    "lc": "de",
                    "cc": country_code.lower(),
                    "fields": OFF_FIELDS,
                }
                try:
                    response = await client.get(f"{catalog_base}/cgi/search.pl", params=params)
                    response.raise_for_status()
                    catalog_payload = response.json()
                    combined_count += int(catalog_payload.get("count") or 0)
                    successful_catalogs.append(catalog_name)
                    for raw in catalog_payload.get("products", []):
                        combined_products.append(
                            {
                                **raw,
                                "_catalog_name": catalog_name,
                                "_catalog_base": catalog_base,
                            }
                        )
                    if len(combined_products) >= page_size:
                        break
                except (httpx.HTTPError, ValueError):
                    continue
        payload = {
            "products": combined_products[:page_size],
            "count": combined_count,
            "catalogs": successful_catalogs,
        }
        if successful_catalogs:
            await db.catalog_cache.update_one(
                {"key": key},
                {
                    "$set": {
                        "key": key,
                        "payload": payload,
                        "expires_at": now + timedelta(hours=CACHE_TTL_HOURS),
                    }
                },
                upsert=True,
            )
            source = " + ".join(successful_catalogs)
        else:
            stale = await db.catalog_cache.find_one({"key": key})
            payload = stale.get("payload") if stale else None
            source = "Open Facts · Offline-Cache" if payload else "MarktFuchs Demo-Katalog"

    products = []
    for raw in (payload or {}).get("products", []):
        catalog_name = str(raw.get("_catalog_name") or "Open Food Facts")
        catalog_base = str(raw.get("_catalog_base") or OPEN_FACTS_CATALOGS["Open Food Facts"])
        product = map_off_product(raw, query, country_code, city, stores, catalog_name, catalog_base)
        if product:
            products.append(product)
    return products, int((payload or {}).get("count") or len(products)), source