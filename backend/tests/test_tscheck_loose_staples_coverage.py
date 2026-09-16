"""tscheck: loose staples across Gemüse/Backwaren/Fleisch/Fisch have curated Grundsortiment offers."""

import pytest

STAPLES = [
    ("Rispentomaten", "basic-rispentomaten"),
    ("Salatgurke", "basic-salatgurke"),
    ("Mischbrot", "basic-mischbrot"),
    ("Hähnchenbrustfilet", "basic-hahnchenbrustfilet"),
    ("Lachsfilet", "basic-lachsfilet"),
]


@pytest.mark.parametrize("query,expected_id", STAPLES)
def test_loose_staple_has_curated_offers_with_address_and_stock(client, query, expected_id):
    response = client.get(
        "/products/search",
        params={"q": query, "country": "DE", "city": "Berlin", "page_size": 12},
    )
    assert response.status_code == 200
    payload = response.json()
    product = next((p for p in payload["results"] if p["id"] == expected_id), None)
    assert product is not None, f"{expected_id} missing from results for query {query!r}"
    assert product["data_source"] == "MarktFuchs Grundsortiment · Demo"
    assert product["offers"], "expected Berlin demo offers"
    for offer in product["offers"]:
        assert offer["address"]
        assert offer["stock_status"] in {"verfügbar", "knapp", "nicht verfügbar"}
