"""Backend coverage: country list includes Germany with local/english name and flag."""


def test_countries_list_contains_germany(client):
    resp = client.get("/locations/countries")
    assert resp.status_code == 200
    countries = resp.json()
    assert len(countries) >= 200  # worldwide selection, seed_facts says 250

    germany = next((c for c in countries if c.get("code") == "DE"), None)
    assert germany is not None, "Germany (DE) must be present in countries list"
    assert germany["local_name"] == "Deutschland"
    assert germany["english_name"] == "Germany"
    assert germany["flag_url"]


def test_countries_search_by_local_or_english_name(client):
    resp = client.get("/locations/countries")
    assert resp.status_code == 200
    countries = resp.json()

    # Simulate the FE search behavior: filter by local or english name (client-side filter)
    matches_local = [c for c in countries if "deutschland" in c["local_name"].lower()]
    matches_english = [c for c in countries if "germany" in c["english_name"].lower()]
    assert any(c["code"] == "DE" for c in matches_local)
    assert any(c["code"] == "DE" for c in matches_english)
