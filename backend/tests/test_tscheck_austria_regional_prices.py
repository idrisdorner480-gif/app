"""Criterion: Die neuen österreichischen Märkte besitzen eigene regionale Demo-Preise.

Searching 'piza' for Innsbruck/AT must surface Wagner pizza with one offer per
Austrian regional chain, and every offer's country_code must be AT.
"""


def test_wagner_pizza_has_offer_per_austrian_chain_in_innsbruck(client):
    response = client.get(
        "/products/search",
        params={"q": "piza", "country": "AT", "city": "Innsbruck"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["country_code"] == "AT"

    wagner = next((p for p in body["results"] if "Wagner" in p["brand"]), None)
    assert wagner is not None, f"Wagner pizza not found in results: {body['results']}"

    expected_stores = {"SPAR", "BILLA", "MPREIS", "BILLA PLUS", "HOFER", "INTERSPAR", "EUROSPAR"}
    offer_stores = {offer["store"] for offer in wagner["offers"]}
    missing = expected_stores - offer_stores
    assert not missing, f"Wagner pizza missing offers for: {missing}; got {offer_stores}"

    for offer in wagner["offers"]:
        assert offer["country_code"] == "AT", f"Unexpected non-AT offer: {offer}"
