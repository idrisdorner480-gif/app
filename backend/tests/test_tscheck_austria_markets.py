"""Criterion: Österreich zeigt die vom Nutzer genannten regionalen Ketten statt nur LIDL und Penny."""


def test_innsbruck_markets_include_regional_chains(client):
    response = client.get("/locations/markets", params={"country": "AT", "city": "Innsbruck"})
    assert response.status_code == 200
    body = response.json()
    assert body["country_code"] == "AT"
    stores = set(body["stores"])
    expected = {"SPAR", "BILLA", "MPREIS", "BILLA PLUS", "HOFER", "INTERSPAR", "EUROSPAR"}
    missing = expected - stores
    assert not missing, f"Innsbruck markets missing expected regional chains: {missing}; got {stores}"
