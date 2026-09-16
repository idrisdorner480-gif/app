"""Backend coverage: region without configured demo markets returns empty results, not foreign offers."""


def test_pizza_search_chicago_us_has_no_demo_markets(client):
    resp = client.get("/products/search", params={"q": "piza", "country": "US", "city": "Chicago"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["results"] == []
    assert data["available_stores"] == []
    assert data["country_code"] == "US"
    assert data["city"] == "Chicago"
