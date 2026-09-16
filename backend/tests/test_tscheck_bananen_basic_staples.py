"""tscheck: Bananen subcategory offers Banane, Bio Banane, Kochbanane + open-facts products."""


def test_bananen_category_has_three_basic_staples(client):
    response = client.get(
        "/products/search",
        params={"q": "Bananen", "category": "bananen", "country": "DE", "city": "Berlin"},
    )
    assert response.status_code == 200
    payload = response.json()
    ids = {product["id"] for product in payload["results"]}
    assert {"basic-banane", "basic-bio-banane", "basic-kochbanane"}.issubset(ids), ids
    for product in payload["results"]:
        if product["id"] in {"basic-banane", "basic-bio-banane", "basic-kochbanane"}:
            assert product["offers"], f"{product['id']} should have Berlin demo offers"
            assert product["category"] == "Obst"
