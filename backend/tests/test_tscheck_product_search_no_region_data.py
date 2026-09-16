"""Backend coverage: region with market chains but no configured demo product prices
returns empty product results (never foreign offers), even though the market register
now lists local chains for that region (per the international market expansion)."""


def test_pizza_search_chicago_us_has_no_demo_prices_yet(client):
    resp = client.get("/products/search", params={"q": "piza", "country": "US", "city": "Chicago"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["results"] == [], "No demo product prices are configured for US yet"
    assert data["country_code"] == "US"
    assert data["city"] == "Chicago"
    # Market register now covers the US, so available_stores is non-empty (chains exist,
    # just no product prices yet) - this is the documented spec_deviation, not a bug.
    assert len(data["available_stores"]) > 0
