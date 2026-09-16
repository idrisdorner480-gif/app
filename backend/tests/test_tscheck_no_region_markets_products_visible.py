"""tscheck: a region with no market register still returns worldwide product data with empty offers."""

import time


def test_region_without_market_register_returns_products_with_empty_offers(client):
    markets = client.get("/locations/markets", params={"country": "BR", "city": "Sao Paulo"})
    assert markets.status_code == 200
    assert markets.json()["stores"] == [], "fixture assumption: BR/Sao Paulo has no demo markets"

    payload = None
    for attempt in range(5):
        response = client.get(
            "/products/search",
            params={"q": "milk", "country": "BR", "city": "Sao Paulo", "page_size": 12},
        )
        assert response.status_code == 200
        candidate = response.json()
        if candidate["results"]:
            payload = candidate
            break
        time.sleep(2)

    assert payload is not None, "Open Food Facts did not return worldwide milk results after retries"
    assert payload["available_stores"] == []
    for product in payload["results"]:
        assert product["offers"] == [], "no regional demo markets registered for BR/Sao Paulo yet"
