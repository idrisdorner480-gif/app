import re
import unicodedata
from difflib import SequenceMatcher

from fastapi import APIRouter, Query

from models.products import Product, ProductSearchResponse, StoreOffer
from lib.regions import available_stores
from lib.product_catalog import attach_branch_to_offer, search_open_food_products
from data.basic_catalog import SEARCH_TERM_BY_SLUG, basic_catalog_products

router = APIRouter(prefix="/products", tags=["products"])


def offer(
    store: str,
    price: float,
    unit_price: float,
    distance_km: float,
    discount_percent: int = 0,
    country_code: str = "DE",
) -> StoreOffer:
    return StoreOffer(
        store=store,
        country_code=country_code,
        price=price,
        unit_price=unit_price,
        distance_km=distance_km,
        discount_percent=discount_percent,
    )


AT_STORE_DISTANCES = {
    "SPAR": 0.6,
    "BILLA": 0.9,
    "MPREIS": 1.3,
    "BILLA PLUS": 2.2,
    "HOFER": 1.7,
    "INTERSPAR": 2.8,
    "EUROSPAR": 1.9,
    "LIDL": 2.4,
    "Penny": 1.5,
}


def austria_offers(prices: dict[str, float], unit_divisor: float) -> list[StoreOffer]:
    lowest_price = min(prices.values())
    return [
        offer(
            store,
            price,
            round(price / unit_divisor, 2),
            AT_STORE_DISTANCES[store],
            18 if price == lowest_price else 0,
            country_code="AT",
        )
        for store, price in prices.items()
    ]


DEMO_PRODUCTS = [
    Product(
        id="red-bull-24er",
        name="Red Bull Energy Drink 24er",
        brand="Red Bull",
        category="Getränke",
        package_size="24 x 250 ml Dosen",
        image_url="https://images.unsplash.com/photo-1612635901022-20ae4c268753?auto=format&fit=crop&w=900&q=85",
        keywords=["red bull", "redbul", "energy", "energydrink", "24er", "dosen", "getränk"],
        offers=[
            offer("REWE", 29.99, 1.25, 0.8, 17),
            offer("EDEKA", 31.49, 1.31, 1.4),
            offer("LIDL", 27.99, 1.17, 2.1, 22),
            offer("ALDI Süd", 28.49, 1.19, 2.8, 12),
        ] + austria_offers({"SPAR": 30.99, "BILLA": 31.49, "MPREIS": 30.49, "BILLA PLUS": 29.99, "HOFER": 27.49, "INTERSPAR": 28.99, "EUROSPAR": 29.49, "LIDL": 27.99, "Penny": 28.49}, 24),
    ),
    Product(
        id="wagner-pizza-salami",
        name="Original Wagner Steinofen Pizza Salami",
        brand="Wagner",
        category="Tiefkühlkost",
        package_size="350 g",
        image_url="https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?auto=format&fit=crop&w=900&q=85",
        keywords=["pizza", "piza", "pizzza", "salami", "tiefkühl", "tk", "wagner"],
        offers=[
            offer("LIDL", 2.49, 7.11, 2.1, 17),
            offer("Penny", 2.69, 7.69, 1.7),
            offer("REWE", 2.99, 8.54, 0.8),
            offer("EDEKA", 3.29, 9.40, 1.4),
        ] + austria_offers({"SPAR": 2.79, "BILLA": 2.99, "MPREIS": 2.89, "BILLA PLUS": 2.69, "HOFER": 2.29, "INTERSPAR": 2.49, "EUROSPAR": 2.59, "LIDL": 2.39, "Penny": 2.49}, 0.35),
    ),
    Product(
        id="dr-oetker-ristorante",
        name="Dr. Oetker Ristorante Pizza Speciale",
        brand="Dr. Oetker",
        category="Tiefkühlkost",
        package_size="320 g",
        image_url="https://images.unsplash.com/photo-1513104890138-7c749659a591?auto=format&fit=crop&w=900&q=85",
        keywords=["pizza", "piza", "ristorante", "speciale", "dr oetker", "tiefkühl"],
        offers=[
            offer("ALDI Süd", 2.29, 7.16, 2.8, 24),
            offer("REWE", 2.79, 8.72, 0.8),
            offer("Kaufland", 2.49, 7.78, 3.2, 11),
        ] + austria_offers({"SPAR": 2.89, "BILLA": 3.19, "MPREIS": 2.99, "BILLA PLUS": 2.79, "HOFER": 2.39, "INTERSPAR": 2.59, "EUROSPAR": 2.69, "LIDL": 2.49, "Penny": 2.59}, 0.32),
    ),
    Product(
        id="ja-vollmilch",
        name="ja! Vollmilch 3,5%",
        brand="ja!",
        category="Molkereiprodukte",
        package_size="1 Liter",
        image_url="https://images.unsplash.com/photo-1563636619-e9143da7973b?auto=format&fit=crop&w=900&q=85",
        keywords=["milch", "milx", "vollmilch", "kuhmilch", "1l", "liter"],
        offers=[
            offer("REWE", 1.09, 1.09, 0.8),
            offer("Penny", 0.99, 0.99, 1.7, 9),
            offer("LIDL", 1.05, 1.05, 2.1),
        ] + austria_offers({"SPAR": 1.29, "BILLA": 1.35, "MPREIS": 1.25, "BILLA PLUS": 1.29, "HOFER": 1.09, "INTERSPAR": 1.19, "EUROSPAR": 1.19, "LIDL": 1.09, "Penny": 1.15}, 1),
    ),
    Product(
        id="barilla-spaghetti",
        name="Barilla Spaghetti No. 5",
        brand="Barilla",
        category="Grundnahrungsmittel",
        package_size="500 g",
        image_url="https://images.unsplash.com/photo-1556761223-4c4282c73f77?auto=format&fit=crop&w=900&q=85",
        keywords=["nudeln", "pasta", "spaghetti", "barila", "barilla", "teigwaren"],
        offers=[
            offer("EDEKA", 1.79, 3.58, 1.4),
            offer("Kaufland", 1.49, 2.98, 3.2, 17),
            offer("REWE", 1.69, 3.38, 0.8),
        ] + austria_offers({"SPAR": 1.89, "BILLA": 1.99, "MPREIS": 1.79, "BILLA PLUS": 1.69, "HOFER": 1.49, "INTERSPAR": 1.59, "EUROSPAR": 1.69, "LIDL": 1.55, "Penny": 1.59}, 0.5),
    ),
    Product(
        id="coca-cola-15l",
        name="Coca-Cola Original Taste",
        brand="Coca-Cola",
        category="Getränke",
        package_size="1,5 Liter PET",
        image_url="https://images.pexels.com/photos/26969901/pexels-photo-26969901.jpeg?auto=compress&cs=tinysrgb&dpr=2&w=900",
        keywords=["cola", "coca cola", "coke", "getränk", "1,5l", "limo"],
        offers=[
            offer("Penny", 1.19, 0.79, 1.7, 20),
            offer("REWE", 1.39, 0.93, 0.8),
            offer("EDEKA", 1.49, 0.99, 1.4),
        ] + austria_offers({"SPAR": 1.49, "BILLA": 1.59, "MPREIS": 1.49, "BILLA PLUS": 1.39, "HOFER": 1.19, "INTERSPAR": 1.29, "EUROSPAR": 1.35, "LIDL": 1.25, "Penny": 1.29}, 1.5),
    ),
    Product(
        id="nutella-450g",
        name="Nutella Nuss-Nugat-Creme",
        brand="Nutella",
        category="Frühstück",
        package_size="450 g Glas",
        image_url="https://images.unsplash.com/photo-1614707267537-2b8a5f5d3a9d?auto=format&fit=crop&w=900&q=85",
        keywords=["nutella", "nutela", "nuss", "nougat", "brotaufstrich", "creme"],
        offers=[
            offer("LIDL", 3.49, 7.76, 2.1, 13),
            offer("REWE", 3.79, 8.42, 0.8),
            offer("ALDI Süd", 3.69, 8.20, 2.8),
        ] + austria_offers({"SPAR": 3.89, "BILLA": 4.09, "MPREIS": 3.99, "BILLA PLUS": 3.79, "HOFER": 3.39, "INTERSPAR": 3.59, "EUROSPAR": 3.69, "LIDL": 3.49, "Penny": 3.59}, 0.45),
    ),
    Product(
        id="bio-aepfel-1kg",
        name="Bio Äpfel süß & knackig",
        brand="REWE Bio",
        category="Obst & Gemüse",
        package_size="1 kg Beutel",
        image_url="https://images.unsplash.com/photo-1683688684067-b87a189c7503?auto=format&fit=crop&w=900&q=85",
        keywords=["apfel", "äpfel", "aepfel", "obst", "bio", "frucht"],
        offers=[
            offer("REWE", 2.49, 2.49, 0.8),
            offer("EDEKA", 2.79, 2.79, 1.4),
            offer("ALDI Süd", 1.99, 1.99, 2.8, 21),
            offer("Penny", 2.29, 2.29, 1.7, 8),
        ] + austria_offers({"SPAR": 2.79, "BILLA": 2.99, "MPREIS": 2.69, "BILLA PLUS": 2.59, "HOFER": 2.19, "INTERSPAR": 2.39, "EUROSPAR": 2.49, "LIDL": 2.29, "Penny": 2.39}, 1),
    ),
]


SYNONYMS = {
    "piza": "pizza",
    "pizaa": "pizza",
    "redbul": "red bull",
    "nutela": "nutella",
    "milx": "milch",
    "aepfel": "äpfel",
    "apfel": "äpfel",
    "cola": "coca cola",
    "nudeln": "spaghetti",
}


def normalize(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value.lower())
    return "".join(char for char in normalized if not unicodedata.combining(char))


def tokens(value: str) -> list[str]:
    return [token for token in re.split(r"[^a-z0-9äöüß]+", normalize(value)) if token]


def similarity(left: str, right: str) -> float:
    left, right = normalize(left), normalize(right)
    if not left or not right:
        return 0
    if left in right or right in left:
        return 1
    return SequenceMatcher(None, left, right).ratio()


def matches(product: Product, query: str) -> bool:
    query_tokens = tokens(query)
    if not query_tokens:
        return True
    searchable = [product.name, product.brand, product.category, *product.keywords]
    searchable_tokens = [token for value in searchable for token in tokens(value)]
    for query_token in query_tokens:
        corrected = SYNONYMS.get(query_token, query_token)
        if any(similarity(corrected, candidate) >= 0.72 for candidate in searchable_tokens):
            continue
        if not any(similarity(query_token, value) >= 0.72 for value in searchable):
            return False
    return True


def corrected_query(query: str) -> str | None:
    normalized_query = normalize(query).strip()
    for typo, correction in SYNONYMS.items():
        if typo in normalized_query and correction not in normalized_query:
            return re.sub(typo, correction, query, flags=re.IGNORECASE)
    return None


@router.get("/search", response_model=ProductSearchResponse)
async def search_products(
    q: str = Query(default="", max_length=80),
    country: str = Query(default="DE", min_length=2, max_length=2),
    city: str = Query(default="Berlin", min_length=1, max_length=120),
    page: int = Query(default=1, ge=1, le=1000),
    page_size: int = Query(default=24, ge=6, le=36),
    category: str | None = Query(default=None, max_length=80),
) -> ProductSearchResponse:
    country_code = country.upper()
    region_stores = available_stores(country_code, city)
    results: list[Product] = []
    for product in DEMO_PRODUCTS:
        offers = [
            attach_branch_to_offer(offer, city, index)
            for index, offer in enumerate(product.offers)
            if offer.country_code == country_code and offer.store in region_stores
        ]
        if page == 1 and offers and not category and matches(product, q):
            results.append(product.model_copy(update={"offers": offers}))
    basic_products, basic_total = basic_catalog_products(
        q,
        category,
        country_code,
        city,
        region_stores,
        page,
        page_size,
    )
    results.extend(basic_products)
    external_query = SEARCH_TERM_BY_SLUG.get(category or "") or corrected_query(q) or q
    external_products, external_total, catalog_source = await search_open_food_products(
        external_query,
        country_code,
        city,
        region_stores,
        page,
        page_size,
    )
    existing_ids = {product.id for product in results}
    results.extend(product for product in external_products if product.id not in existing_ids)
    total = external_total + basic_total + (len(results) - len(external_products) - len(basic_products) if page == 1 else 0)
    return ProductSearchResponse(
        query=q,
        corrected_query=corrected_query(q),
        results=results,
        total=total,
        data_source="Produktstammdaten: Open Food Facts · Preise & Filialbestände: Demo",
        country_code=country_code,
        city=city,
        available_stores=region_stores,
        page=page,
        page_size=page_size,
        has_more=page * page_size < external_total or page * page_size < basic_total,
        catalog_source=catalog_source,
    )
