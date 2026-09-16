"""Backend coverage: cities endpoint is scoped to the requested country (DE -> Berlin)."""


def test_cities_for_germany_include_berlin(client):
    resp = client.get("/locations/cities", params={"country": "DE"})
    assert resp.status_code == 200
    cities = resp.json()
    assert len(cities) > 0
    names = [c["name"] for c in cities]
    assert "Berlin" in names


def test_cities_for_germany_do_not_include_foreign_city(client):
    resp = client.get("/locations/cities", params={"country": "DE"})
    assert resp.status_code == 200
    cities = resp.json()
    names = [c["name"] for c in cities]
    # Chicago is a US city and must not leak into Germany's city list
    assert "Chicago" not in names
