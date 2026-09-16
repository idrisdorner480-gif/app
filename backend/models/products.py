from pydantic import BaseModel, Field
from typing import List


class StoreOffer(BaseModel):
    store: str
    country_code: str
    price: float
    unit_price: float
    distance_km: float
    available: bool = True
    discount_percent: int = 0


class Product(BaseModel):
    id: str
    name: str
    brand: str
    category: str
    package_size: str
    image_url: str
    keywords: List[str] = Field(default_factory=list)
    offers: List[StoreOffer]


class ProductSearchResponse(BaseModel):
    query: str
    corrected_query: str | None = None
    results: List[Product]
    total: int
    data_source: str
    country_code: str
    city: str
    available_stores: List[str] = Field(default_factory=list)