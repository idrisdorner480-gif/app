"""Criterion: Deutsche Angebote werden nicht mit österreichischen Ketten vermischt.

Berlin/DE pizza offers must be exclusively country_code DE and must not contain any
Austria-only chains (MPREIS, BILLA, HOFER, INTERSPAR, EUROSPAR).
"""


def test_berlin_pizza_offers_are_de_only(client):
    response = client.get(
        "/products/search",
        params={"q": "piza", "country": "DE", "city": "Berlin"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["country_code"] == "DE"

    austrian_only_chains = {"MPREIS", "BILLA", "HOFER", "INTERSPAR", "EUROSPAR"}
    for product in body["results"]:
        for offer in product["offers"]:
            assert offer["country_code"] == "DE", f"Non-DE offer leaked into Berlin results: {offer}"
            assert offer["store"] not in austrian_only_chains, f"Austrian chain leaked into Berlin: {offer}"
