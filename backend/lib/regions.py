COUNTRY_STORES: dict[str, list[str]] = {
    "DE": ["REWE", "EDEKA", "LIDL", "ALDI Süd", "Penny", "Kaufland"],
    "AT": ["SPAR", "BILLA", "MPREIS", "BILLA PLUS", "HOFER", "INTERSPAR", "EUROSPAR", "LIDL", "Penny"],
    "CH": ["Coop", "Migros", "Denner", "LIDL", "ALDI Suisse"],
    "FR": ["Carrefour", "E.Leclerc", "Intermarché", "Auchan", "LIDL", "Monoprix"],
    "IT": ["Conad", "Coop Italia", "Esselunga", "LIDL", "Eurospin", "Carrefour"],
    "ES": ["Mercadona", "Carrefour", "LIDL", "DIA", "Alcampo", "Eroski"],
    "NL": ["Albert Heijn", "Jumbo", "LIDL", "PLUS", "Aldi"],
    "BE": ["Colruyt", "Delhaize", "Carrefour", "LIDL", "Aldi"],
    "PL": ["Biedronka", "LIDL", "Kaufland", "Carrefour", "Auchan", "Żabka"],
    "CZ": ["Albert", "LIDL", "Kaufland", "Tesco", "Billa", "Penny Market"],
    "SK": ["Tesco", "LIDL", "Kaufland", "Billa", "COOP Jednota"],
    "HU": ["Tesco", "LIDL", "Aldi", "SPAR", "Penny Market", "Auchan"],
    "PT": ["Continente", "Pingo Doce", "LIDL", "Auchan", "Intermarché"],
    "GB": ["Tesco", "Sainsbury's", "Asda", "Morrisons", "Aldi", "Lidl", "Waitrose"],
    "IE": ["Tesco", "Dunnes Stores", "SuperValu", "Aldi", "Lidl"],
    "US": ["Walmart", "Kroger", "Costco", "Target", "Whole Foods", "Trader Joe's", "Aldi"],
    "CA": ["Loblaws", "Sobeys", "Walmart", "Costco", "Metro", "No Frills"],
    "AU": ["Woolworths", "Coles", "Aldi", "IGA"],
    "NZ": ["Woolworths", "New World", "PAK'nSAVE", "Four Square"],
    "TR": ["Migros", "BİM", "A101", "ŞOK", "CarrefourSA"],
    "SE": ["ICA", "Coop", "Willys", "Hemköp", "Lidl"],
    "NO": ["Kiwi", "Rema 1000", "Coop", "Meny", "Bunnpris"],
    "DK": ["Netto", "Rema 1000", "Coop 365", "Føtex", "Bilka", "Lidl"],
    "FI": ["K-Citymarket", "K-Supermarket", "Prisma", "S-market", "Lidl"],
    "JP": ["AEON", "Ito-Yokado", "Seiyu", "Life", "Maruetsu"],
    "IN": ["Reliance Smart", "DMart", "Spencer's", "More", "Star Bazaar"],
}

CITY_STORE_OVERRIDES: dict[tuple[str, str], list[str]] = {
    ("DE", "Berlin"): ["REWE", "EDEKA", "LIDL", "ALDI Süd", "Penny", "Kaufland"],
    ("DE", "München"): ["REWE", "EDEKA", "LIDL", "ALDI Süd", "Penny"],
    ("DE", "Hamburg"): ["REWE", "EDEKA", "LIDL", "ALDI Süd", "Penny", "Kaufland"],
    ("DE", "Köln"): ["REWE", "EDEKA", "LIDL", "ALDI Süd", "Penny", "Kaufland"],
    ("AT", "Wien"): ["SPAR", "BILLA", "BILLA PLUS", "HOFER", "INTERSPAR", "EUROSPAR", "LIDL", "Penny"],
    ("AT", "Vienna"): ["SPAR", "BILLA", "BILLA PLUS", "HOFER", "INTERSPAR", "EUROSPAR", "LIDL", "Penny"],
    ("AT", "Graz"): ["SPAR", "BILLA", "BILLA PLUS", "HOFER", "INTERSPAR", "EUROSPAR", "LIDL", "Penny"],
    ("AT", "Linz"): ["SPAR", "BILLA", "BILLA PLUS", "HOFER", "INTERSPAR", "EUROSPAR", "LIDL", "Penny"],
    ("AT", "Innsbruck"): ["SPAR", "BILLA", "MPREIS", "BILLA PLUS", "HOFER", "INTERSPAR", "EUROSPAR", "LIDL"],
    ("AT", "Salzburg"): ["SPAR", "BILLA", "BILLA PLUS", "HOFER", "INTERSPAR", "EUROSPAR", "LIDL", "Penny"],
}


def available_stores(country_code: str, city: str) -> list[str]:
    code = country_code.upper()
    return CITY_STORE_OVERRIDES.get((code, city), COUNTRY_STORES.get(code, []))