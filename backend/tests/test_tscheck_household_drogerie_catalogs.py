"""tscheck: Haushalt (Waschmittel) uses Open Products Facts, Drogerie (Shampoo) uses Open Beauty Facts.

FIXED (iteration 4 retest): lib/product_catalog.py used to hardcode
`source = "Open Food Facts · Cache" if payload else "Open Food Facts"` BEFORE checking
whether the payload came from an existing cache hit, discarding the true catalogs list on
cache hits. It has since been fixed to re-derive the label from the cached payload's
`catalogs` field, so a cached call still reports a source string containing "Open Products
Facts" (optionally suffixed with "· Cache"), never the generic "Open Food Facts · Cache".
"""

import asyncio
import os
from pathlib import Path

from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

load_dotenv(Path(__file__).resolve().parents[1] / ".env")


async def _clear_cache(pattern: str) -> None:
    # Fresh client bound to *this* test's event loop - the shared lib.db handle is bound to
    # whichever loop first touched it and breaks across pytest-asyncio's per-test loops.
    local_client = AsyncIOMotorClient(os.environ["MONGO_URL"])
    try:
        local_db = local_client[os.environ["DB_NAME"]]
        await local_db.catalog_cache.delete_many({"key": {"$regex": pattern}})
    finally:
        local_client.close()


async def _search_with_retry(aclient, **params):
    payload = None
    for _ in range(4):
        response = await aclient.get("/products/search", params=params)
        assert response.status_code == 200
        candidate = response.json()
        if candidate["results"]:
            payload = candidate
            break
        await asyncio.sleep(2)
    return payload


async def test_waschmittel_fresh_fetch_uses_open_products_facts(aclient):
    await _clear_cache("laundry detergents")
    payload = await _search_with_retry(
        aclient, q="Waschmittel", category="waschmittel", country="DE", city="Berlin", page_size=12
    )
    assert payload is not None, "no Waschmittel results after retries"
    assert payload["catalog_source"] in {"Open Products Facts", "Open Products Facts + Open Food Facts"}
    for product in payload["results"]:
        assert product["offers"], "expected Berlin demo offers"
        for offer in product["offers"]:
            assert offer["address"]


async def test_shampoo_fresh_fetch_uses_open_beauty_facts(aclient):
    await _clear_cache("shampoos")
    payload = await _search_with_retry(
        aclient, q="Shampoo", category="shampoo", country="DE", city="Berlin", page_size=12
    )
    assert payload is not None, "no Shampoo results after retries"
    assert payload["catalog_source"] in {
        "Open Beauty Facts",
        "Open Beauty Facts + Open Products Facts",
        "Open Beauty Facts + Open Food Facts",
    }
    for product in payload["results"]:
        assert product["offers"]
        for offer in product["offers"]:
            assert offer["stock_status"] in {"verfügbar", "knapp", "nicht verfügbar"}


async def test_cached_waschmittel_catalog_source_label_is_correct(aclient):
    """Regression guard: cached Waschmittel calls must keep the Open Products Facts
    attribution (optionally with a '· Cache' suffix), never fall back to the generic
    'Open Food Facts · Cache' mislabel."""
    await _clear_cache("laundry detergents")
    first = await _search_with_retry(
        aclient, q="Waschmittel", category="waschmittel", country="DE", city="Berlin", page_size=12
    )
    assert first is not None
    assert first["catalog_source"] in {"Open Products Facts", "Open Products Facts + Open Food Facts"}
    true_source = first["catalog_source"]

    second = await aclient.get(
        "/products/search",
        params={"q": "Waschmittel", "category": "waschmittel", "country": "DE", "city": "Berlin", "page_size": 12},
    )
    assert second.status_code == 200
    second_payload = second.json()
    cached_source = second_payload["catalog_source"]
    base_source = cached_source.replace(" · Cache", "")
    assert base_source == true_source, (
        f"cached call mislabeled catalog_source as {cached_source!r} "
        f"instead of the true source {true_source!r} (optionally with '· Cache' suffix)"
    )
    assert cached_source != "Open Food Facts · Cache", (
        "cached call regressed to the generic 'Open Food Facts · Cache' mislabel"
    )
    assert "Open Products Facts" in cached_source
