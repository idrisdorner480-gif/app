import re
import unicodedata
from difflib import SequenceMatcher

from fastapi import APIRouter, Query

from models.products import Product, ProductSearchResponse, StoreOffer

router = APIRouter(prefix="/products", tags=["products"])


def offer(store: str, price: float, unit_price: float, distance_km: float, discount_percent: int = 0) -> StoreOffer:
    return StoreOffer(
        store=store,
        price=price,
        unit_price=unit_price,
        distance_km=distance_km,
        discount_percent=discount_percent,
    )


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
        ],
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
        ],
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
        ],
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
        ],
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
        ],
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
        ],
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
        ],
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
        ],
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
async def search_products(q: str = Query(default="", max_length=80)) -> ProductSearchResponse:
    results = [product for product in DEMO_PRODUCTS if matches(product, q)]
    return ProductSearchResponse(
        query=q,
        corrected_query=corrected_query(q),
        results=results,
        total=len(results),
        data_source="Demo-Angebote · lokale Marktbeispiele",
    )
