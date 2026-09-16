from fastapi import APIRouter

from data.basic_catalog import CATEGORIES
from models.catalog import CatalogCategory

router = APIRouter(prefix="/catalog", tags=["catalog"])


@router.get("/categories", response_model=list[CatalogCategory])
async def get_catalog_categories() -> list[CatalogCategory]:
    return CATEGORIES