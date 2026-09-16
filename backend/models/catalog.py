from pydantic import BaseModel, Field


class CatalogSubcategory(BaseModel):
    slug: str
    name: str
    search_term: str


class CatalogCategory(BaseModel):
    slug: str
    name: str
    description: str
    icon: str
    subcategories: list[CatalogSubcategory] = Field(default_factory=list)