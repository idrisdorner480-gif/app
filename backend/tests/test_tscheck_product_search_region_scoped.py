"""Backend coverage: product search is scoped to region-approved stores (Berlin/DE)."""

ALLOWED_BERLIN_STORES = {"REWE", "EDEKA", "LIDL", "ALDI Süd", "Penny", "Kaufland"}


def test_pizza_search_berlin_only_approved_stores(client):
    resp = client.get("/products/search", params={"q": "piza", "country": "DE", "city": "Berlin"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["corrected_query"] == "pizza"
    assert len(data["results"]) > 0

    # every offer store must be within the approved set for this region
    stores_in_offers = set()
    for result in data["results"]:
        for offer in result["offers"]:
            stores_in_offers.add(offer["store"])
    assert stores_in_offers, "expected at least one offer"
    assert stores_in_offers.issubset(ALLOWED_BERLIN_STORES), (
        f"unexpected stores outside region allowlist: {stores_in_offers - ALLOWED_BERLIN_STORES}"
    )

    # available_stores metadata should also match the approved allowlist exactly
    assert set(data["available_stores"]) == ALLOWED_BERLIN_STORES
