import asyncio
import time
from typing import Any

import httpx
from fastapi import APIRouter, HTTPException, Query

from lib.regions import available_stores
from models.locations import City, Country, RegionMarkets

router = APIRouter(prefix="/locations", tags=["locations"])

COUNTRIES_URL = "https://countries.dev/countries"
CITIES_URL = "https://countries.dev/cities"
CACHE_TTL_SECONDS = 86_400
_cache: dict[str, tuple[float, Any]] = {}

FALLBACK_COUNTRIES = [
    Country(code="DE", local_name="Deutschland", english_name="Germany", flag_url="https://flagcdn.com/de.svg"),
    Country(code="AT", local_name="Österreich", english_name="Austria", flag_url="https://flagcdn.com/at.svg"),
    Country(code="CH", local_name="Schweiz", english_name="Switzerland", flag_url="https://flagcdn.com/ch.svg"),
    Country(code="FR", local_name="France", english_name="France", flag_url="https://flagcdn.com/fr.svg"),
    Country(code="IT", local_name="Italia", english_name="Italy", flag_url="https://flagcdn.com/it.svg"),
    Country(code="ES", local_name="España", english_name="Spain", flag_url="https://flagcdn.com/es.svg"),
    Country(code="NL", local_name="Nederland", english_name="Netherlands", flag_url="https://flagcdn.com/nl.svg"),
    Country(code="PL", local_name="Polska", english_name="Poland", flag_url="https://flagcdn.com/pl.svg"),
    Country(code="TR", local_name="Türkiye", english_name="Turkey", flag_url="https://flagcdn.com/tr.svg"),
    Country(code="GB", local_name="United Kingdom", english_name="United Kingdom", flag_url="https://flagcdn.com/gb.svg"),
    Country(code="US", local_name="United States", english_name="United States", flag_url="https://flagcdn.com/us.svg"),
    Country(code="CA", local_name="Canada", english_name="Canada", flag_url="https://flagcdn.com/ca.svg"),
]

FALLBACK_CITIES: dict[str, list[str]] = {
    "DE": ["Berlin", "Hamburg", "München", "Köln", "Frankfurt am Main", "Stuttgart", "Düsseldorf", "Leipzig"],
    "AT": ["Wien", "Graz", "Linz", "Salzburg", "Innsbruck"],
    "CH": ["Zürich", "Genève", "Basel", "Bern", "Lausanne"],
    "FR": ["Paris", "Marseille", "Lyon", "Toulouse", "Nice"],
    "IT": ["Roma", "Milano", "Napoli", "Torino", "Firenze"],
    "ES": ["Madrid", "Barcelona", "València", "Sevilla", "Bilbao"],
    "NL": ["Amsterdam", "Rotterdam", "Den Haag", "Utrecht", "Eindhoven"],
    "PL": ["Warszawa", "Kraków", "Łódź", "Wrocław", "Gdańsk"],
    "TR": ["İstanbul", "Ankara", "İzmir", "Bursa", "Antalya"],
    "GB": ["London", "Birmingham", "Manchester", "Glasgow", "Liverpool"],
    "US": ["New York City", "Los Angeles", "Chicago", "Houston", "Phoenix"],
    "CA": ["Toronto", "Montréal", "Vancouver", "Calgary", "Ottawa"],
}


async def fetch_json(key: str, url: str, params: dict[str, str]) -> Any:
    cached = _cache.get(key)
    if cached and time.time() - cached[0] < CACHE_TTL_SECONDS:
        return cached[1]
    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(8.0, connect=3.0)) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            payload = response.json()
            _cache[key] = (time.time(), payload)
            return payload
    except (httpx.HTTPError, ValueError, asyncio.TimeoutError):
        if cached:
            return cached[1]
        return None


def country_from_raw(item: dict[str, Any]) -> Country | None:
    code = item.get("alpha2Code") or item.get("cca2")
    names = item.get("name", {})
    english_name = names if isinstance(names, str) else names.get("common")
    if not code or not english_name:
        return None
    native_name = item.get("nativeName")
    local_name = native_name if isinstance(native_name, str) and native_name else english_name
    if not native_name and isinstance(names, dict):
        native_names = names.get("nativeName") or {}
        if native_names:
            first_native = next(iter(native_names.values()))
            local_name = first_native.get("common", english_name)
    flags = item.get("flags") or {}
    return Country(
        code=code,
        local_name=local_name,
        english_name=english_name,
        flag_url=flags.get("svg") or flags.get("png") or f"https://flagcdn.com/{code.lower()}.svg",
    )


@router.get("/countries", response_model=list[Country])
async def get_countries() -> list[Country]:
    payload = await fetch_json(
        "countries-v1",
        COUNTRIES_URL,
        {"limit": "300", "full": "true"},
    )
    countries = [country for item in (payload or []) if (country := country_from_raw(item))]
    if not countries:
        countries = FALLBACK_COUNTRIES
    return sorted(countries, key=lambda country: country.local_name.casefold())


@router.get("/cities", response_model=list[City])
async def get_cities(country: str = Query(min_length=2, max_length=2)) -> list[City]:
    code = country.upper()
    if not code.isalpha():
        raise HTTPException(status_code=400, detail="Ungültiger Ländercode")
    payload = await fetch_json(
        f"cities-{code}-v1",
        CITIES_URL,
        {"country": code, "limit": "100"},
    )
    raw_cities = payload if isinstance(payload, list) else (payload or {}).get("data", [])
    cities: list[City] = []
    for index, item in enumerate(raw_cities):
        if not isinstance(item, dict) or not item.get("name"):
            continue
        cities.append(
            City(
                id=str(item.get("geonameId") or item.get("id") or f"{code}-{index}"),
                name=str(item["name"]),
                population=int(item.get("population") or 0),
            )
        )
    if not cities:
        cities = [City(id=f"{code}-{index}", name=name) for index, name in enumerate(FALLBACK_CITIES.get(code, []))]
    return sorted(cities, key=lambda city: (-city.population, city.name.casefold()))


@router.get("/markets", response_model=RegionMarkets)
async def get_region_markets(
    country: str = Query(min_length=2, max_length=2),
    city: str = Query(min_length=1, max_length=120),
) -> RegionMarkets:
    code = country.upper()
    return RegionMarkets(
        country_code=code,
        city=city,
        stores=available_stores(code, city),
        data_source="Regionale Marktfreigabe · Demo",
    )