from pydantic import BaseModel, Field
from typing import List, Literal


class StoreOffer(BaseModel):
    store: str
    country_code: str
    branch_id: str = ""
    branch_name: str = ""
    address: str = ""
    price: float
    unit_price: float
    distance_km: float
    available: bool = True
    stock_status: Literal["verfügbar", "knapp", "nicht verfügbar"] = "verfügbar"
    discount_percent: int = 0


class Product(BaseModel):
    id: str
    name: str
    brand: str
    category: str
    package_size: str
    image_url: str
    barcode: str | None = None
    data_source: str = "MarktFuchs Demo-Katalog"
    product_url: str | None = None
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
    page: int = 1
    page_size: int = 24
    has_more: bool = False
    catalog_source: str = "MarktFuchs Demo-Katalog"