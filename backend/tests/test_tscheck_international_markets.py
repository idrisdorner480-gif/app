"""Criterion: Das Marktregister deckt zusätzlich mehrere große internationale Regionen ab.

Market queries for France/Paris, USA/Chicago, UK/London and Switzerland/Zürich must
each return several country-typical chains instead of empty lists.
"""

import pytest

REGIONS = [
    ("FR", "Paris", {"Carrefour", "E.Leclerc", "Auchan"}),
    ("US", "Chicago", {"Walmart", "Kroger", "Costco"}),
    ("GB", "London", {"Tesco", "Sainsbury's", "Asda"}),
    ("CH", "Zürich", {"Coop", "Migros"}),
]


@pytest.mark.parametrize("country,city,expected_subset", REGIONS)
def test_region_markets_have_local_chains(client, country, city, expected_subset):
    response = client.get("/locations/markets", params={"country": country, "city": city})
    assert response.status_code == 200
    body = response.json()
    stores = set(body["stores"])
    assert len(stores) >= 3, f"{country}/{city} returned too few stores: {stores}"
    overlap = expected_subset & stores
    assert overlap, f"{country}/{city} missing expected local chains {expected_subset}, got {stores}"
