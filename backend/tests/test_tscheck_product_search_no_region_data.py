"""Backend coverage: region with market chains (US/Chicago) now surfaces the worldwide Open
Facts catalog for any query, with regional demo offers attached where available - this is
the documented spec_deviation from this iteration (catalog products stay visible even when
a region previously had no configured demo product prices), not a regression of the older
"no foreign offers" guarantee."""

import time


def test_pizza_search_chicago_us_returns_worldwide_catalog_with_us_offers(client):
    payload = None
    for _ in range(5):
        resp = client.get(
            "/products/search",
            params={"q": "piza", "country": "US", "city": "Chicago", "page_size": 12},
        )
        assert resp.status_code == 200
        candidate = resp.json()
        if candidate["results"]:
            payload = candidate
            break
        time.sleep(2)
    assert payload is not None, "Open Food Facts did not return pizza results after retries"

    assert payload["country_code"] == "US"
    assert payload["city"] == "Chicago"
    # Market register now covers the US, so available_stores is non-empty.
    assert len(payload["available_stores"]) > 0
    # Every offer attached to a result must belong to the US region - never foreign stores.
    for product in payload["results"]:
        for offer in product["offers"]:
            assert offer["country_code"] == "US"
            assert offer["store"] in payload["available_stores"]
