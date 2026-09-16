"""Criterion: Regionale Verfügbarkeit unterscheidet österreichische Städte sinnvoll.

Innsbruck has MPREIS; Vienna does not, but has the other AT chains plus LIDL/Penny.
"""


def test_innsbruck_has_mpreis(client):
    response = client.get("/locations/markets", params={"country": "AT", "city": "Innsbruck"})
    assert response.status_code == 200
    assert "MPREIS" in response.json()["stores"]


def test_vienna_has_no_mpreis_but_has_other_chains(client):
    response = client.get("/locations/markets", params={"country": "AT", "city": "Vienna"})
    assert response.status_code == 200
    stores = set(response.json()["stores"])
    assert "MPREIS" not in stores, f"Vienna should not include MPREIS, got: {stores}"
    expected = {"SPAR", "BILLA", "BILLA PLUS", "HOFER", "INTERSPAR", "EUROSPAR", "LIDL", "Penny"}
    missing = expected - stores
    assert not missing, f"Vienna missing expected chains: {missing}; got {stores}"
