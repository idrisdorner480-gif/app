"""tscheck: packaged goods/beverages load worldwide paginated Open Facts results.

The upstream Open Food Facts API is occasionally flaky (intermittent 503s), so fetching a
result set retries a few times. Once results ARE returned, this asserts the response shape
that the UI depends on for pagination (total, catalog_source, has_more, per-offer country).
"""

import time


def _search(client, **params):
    return client.get("/products/search", params=params)


def _search_until_populated(client, retries=6, **params):
    payload = None
    for _ in range(retries):
        response = _search(client, **params)
        assert response.status_code == 200
        candidate = response.json()
        if candidate["total"] > 0 and candidate["results"]:
            payload = candidate
            break
        time.sleep(2)
    return payload


def test_us_chicago_limonaden_returns_many_open_food_facts_results(client):
    payload = _search_until_populated(
        client,
        q="limonaden",
        category="limonaden",
        country="US",
        city="Chicago",
        page=1,
        page_size=24,
    )
    assert payload is not None, "Open Food Facts did not return limonaden results after retries"

    assert payload["catalog_source"].startswith("Open Food Facts")
    assert payload["total"] > payload["page_size"], "total should exceed a single page for pagination"

    first_product = payload["results"][0]
    assert first_product["image_url"]
    assert first_product["data_source"]
    assert first_product["offers"], "expected regional demo offers for Chicago"
    for offer in first_product["offers"]:
        assert offer["country_code"] == "US"


def test_us_chicago_limonaden_next_page_is_reachable(client):
    """Regression guard: `has_more` must reflect that total (~600+) vastly exceeds one page.

    KNOWN BUG (see test report): when Open Food Facts returns one item OFF filters out
    (missing name/code) on a fetch, the API undercounts that page's results below
    `page_size` and computes has_more=False even though `total` is in the hundreds - and
    this incomplete result gets cached for 12h, so the UI's "Weitere Produkte" button stays
    disabled. This test intentionally fails while that logic bug is present.
    """
    payload = _search_until_populated(
        client,
        q="limonaden",
        category="limonaden",
        country="US",
        city="Chicago",
        page=1,
        page_size=24,
    )
    assert payload is not None, "Open Food Facts did not return limonaden results after retries"
    assert payload["total"] > payload["page_size"]
    assert payload["has_more"] is True, (
        f"has_more is False despite total={payload['total']} far exceeding page_size="
        f"{payload['page_size']} (got {len(payload['results'])} mapped results) - pagination "
        "is not actually reachable from the UI for this region/category."
    )
