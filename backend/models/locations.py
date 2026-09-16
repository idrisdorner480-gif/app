from pydantic import BaseModel, Field


class Country(BaseModel):
    code: str
    local_name: str
    english_name: str
    flag_url: str


class City(BaseModel):
    id: str
    name: str
    population: int = 0


class RegionMarkets(BaseModel):
    country_code: str
    city: str
    stores: list[str] = Field(default_factory=list)
    data_source: str