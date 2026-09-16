COUNTRY_STORES: dict[str, list[str]] = {
    "DE": ["REWE", "EDEKA", "LIDL", "ALDI Süd", "Penny", "Kaufland"],
    "AT": ["LIDL", "Penny"],
}

CITY_STORE_OVERRIDES: dict[tuple[str, str], list[str]] = {
    ("DE", "Berlin"): ["REWE", "EDEKA", "LIDL", "ALDI Süd", "Penny", "Kaufland"],
    ("DE", "München"): ["REWE", "EDEKA", "LIDL", "ALDI Süd", "Penny"],
    ("DE", "Hamburg"): ["REWE", "EDEKA", "LIDL", "ALDI Süd", "Penny", "Kaufland"],
    ("DE", "Köln"): ["REWE", "EDEKA", "LIDL", "ALDI Süd", "Penny", "Kaufland"],
    ("AT", "Wien"): ["LIDL", "Penny"],
    ("AT", "Graz"): ["LIDL", "Penny"],
}


def available_stores(country_code: str, city: str) -> list[str]:
    code = country_code.upper()
    return CITY_STORE_OVERRIDES.get((code, city), COUNTRY_STORES.get(code, []))