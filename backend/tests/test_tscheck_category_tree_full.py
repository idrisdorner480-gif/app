"""tscheck: full category tree with real subcategories (not just apple chips)."""

EXPECTED_MAIN_CATEGORIES = {
    "obst",
    "gemuese",
    "getraenke",
    "milchprodukte",
    "tiefkuehl",
    "backwaren",
    "fleisch",
    "fisch",
    "vegan",
    "vorrat",
    "haushalt",
    "drogerie",
}

EXPECTED_OBST_SUBCATEGORIES = {
    "aepfel",
    "bananen",
    "beeren",
    "zitrusfruechte",
    "trauben",
    "birnen",
    "steinobst",
    "tropenfruechte",
    "melonen",
}


def test_categories_endpoint_returns_all_twelve_main_categories(client):
    response = client.get("/catalog/categories")
    assert response.status_code == 200
    payload = response.json()
    slugs = {category["slug"] for category in payload}
    assert EXPECTED_MAIN_CATEGORIES.issubset(slugs), (
        f"missing categories: {EXPECTED_MAIN_CATEGORIES - slugs}"
    )
    # every category must expose at least one selectable subcategory
    for category in payload:
        assert len(category["subcategories"]) >= 1, category["slug"]


def test_obst_category_is_not_limited_to_apples(client):
    response = client.get("/catalog/categories")
    assert response.status_code == 200
    payload = response.json()
    obst = next(category for category in payload if category["slug"] == "obst")
    sub_slugs = {sub["slug"] for sub in obst["subcategories"]}
    assert EXPECTED_OBST_SUBCATEGORIES.issubset(sub_slugs), (
        f"missing obst subcategories: {EXPECTED_OBST_SUBCATEGORIES - sub_slugs}"
    )
