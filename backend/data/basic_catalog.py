import re
import unicodedata

from lib.product_catalog import demo_branch_offers
from models.catalog import CatalogCategory, CatalogSubcategory
from models.products import Product

CATEGORY_IMAGES = {
    "obst": "https://images.unsplash.com/photo-1610832958506-aa56368176cf?auto=format&fit=crop&w=900&q=82",
    "gemuese": "https://images.unsplash.com/photo-1566385101042-1a0aa0c1268c?auto=format&fit=crop&w=900&q=82",
    "getraenke": "https://images.unsplash.com/photo-1544145945-f90425340c7e?auto=format&fit=crop&w=900&q=82",
    "milchprodukte": "https://images.unsplash.com/photo-1628088062854-d1870b4553da?auto=format&fit=crop&w=900&q=82",
    "tiefkuehl": "https://images.unsplash.com/photo-1578662996442-48f60103fc96?auto=format&fit=crop&w=900&q=82",
    "backwaren": "https://images.unsplash.com/photo-1509440159596-0249088772ff?auto=format&fit=crop&w=900&q=82",
    "fleisch": "https://images.unsplash.com/photo-1607623814075-e51df1bdc82f?auto=format&fit=crop&w=900&q=82",
    "fisch": "https://images.unsplash.com/photo-1544551763-46a013bb70d5?auto=format&fit=crop&w=900&q=82",
    "vegan": "https://images.unsplash.com/photo-1512621776951-a57141f2eefd?auto=format&fit=crop&w=900&q=82",
    "vorrat": "https://images.unsplash.com/photo-1583258292688-d0213dc5a3a8?auto=format&fit=crop&w=900&q=82",
    "haushalt": "https://images.unsplash.com/photo-1563453392212-326f5e854473?auto=format&fit=crop&w=900&q=82",
    "drogerie": "https://images.unsplash.com/photo-1556228578-8c89e6adf883?auto=format&fit=crop&w=900&q=82",
}


def sub(slug: str, name: str, search_term: str | None = None) -> CatalogSubcategory:
    return CatalogSubcategory(slug=slug, name=name, search_term=search_term or name)


CATEGORIES = [
    CatalogCategory(slug="obst", name="Obst", description="Frisch, lose und verpackt", icon="apple", subcategories=[sub("aepfel", "Äpfel"), sub("bananen", "Bananen"), sub("beeren", "Beeren"), sub("zitrusfruechte", "Zitrusfrüchte"), sub("trauben", "Trauben"), sub("birnen", "Birnen"), sub("steinobst", "Steinobst"), sub("tropenfruechte", "Tropenfrüchte"), sub("melonen", "Melonen")]),
    CatalogCategory(slug="gemuese", name="Gemüse", description="Frisches Gemüse und Kräuter", icon="carrot", subcategories=[sub("tomaten", "Tomaten"), sub("gurken", "Gurken"), sub("paprika", "Paprika"), sub("kartoffeln", "Kartoffeln"), sub("zwiebeln", "Zwiebeln"), sub("wurzelgemuese", "Wurzelgemüse"), sub("salate", "Salate"), sub("kohl", "Kohl"), sub("pilze", "Pilze"), sub("kraeuter", "Kräuter")]),
    CatalogCategory(slug="getraenke", name="Getränke", description="Wasser, Säfte, Kaffee und mehr", icon="cup-soda", subcategories=[sub("wasser", "Wasser"), sub("saefte", "Säfte"), sub("limonaden", "Limonaden"), sub("energy", "Energy Drinks"), sub("kaffee", "Kaffee"), sub("tee", "Tee"), sub("bier", "Bier"), sub("wein", "Wein"), sub("pflanzendrinks", "Pflanzendrinks")]),
    CatalogCategory(slug="milchprodukte", name="Milchprodukte & Eier", description="Milch, Käse, Joghurt und Eier", icon="milk", subcategories=[sub("milch", "Milch"), sub("joghurt", "Joghurt"), sub("kaese", "Käse"), sub("butter", "Butter"), sub("sahne", "Sahne"), sub("eier", "Eier")]),
    CatalogCategory(slug="tiefkuehl", name="Tiefkühl", description="Pizza, Gemüse, Eis und Fertiggerichte", icon="snowflake", subcategories=[sub("pizza", "Pizza"), sub("tiefkuehlgemuese", "Tiefkühlgemüse"), sub("eis", "Speiseeis"), sub("tiefkuehlgerichte", "Tiefkühlgerichte"), sub("tiefkuehlfisch", "Tiefkühlfisch")]),
    CatalogCategory(slug="backwaren", name="Backwaren", description="Brot, Gebäck und frische Backwaren", icon="croissant", subcategories=[sub("brot", "Brot"), sub("broetchen", "Brötchen"), sub("gebaeck", "Gebäck"), sub("kuchen", "Kuchen"), sub("toast", "Toast")]),
    CatalogCategory(slug="fleisch", name="Fleisch & Wurst", description="Frischfleisch, Geflügel und Wurst", icon="beef", subcategories=[sub("rind", "Rindfleisch"), sub("schwein", "Schweinefleisch"), sub("gefluegel", "Geflügel"), sub("hackfleisch", "Hackfleisch"), sub("wurst", "Wurst & Aufschnitt")]),
    CatalogCategory(slug="fisch", name="Fisch & Meeresfrüchte", description="Frischer Fisch und Meeresfrüchte", icon="fish", subcategories=[sub("lachs", "Lachs"), sub("weissfisch", "Weißfisch"), sub("thunfisch", "Thunfisch"), sub("garnelen", "Garnelen"), sub("muscheln", "Muscheln")]),
    CatalogCategory(slug="vegan", name="Vegan & vegetarisch", description="Pflanzliche Alternativen", icon="leaf", subcategories=[sub("tofu", "Tofu"), sub("fleischersatz", "Fleischersatz"), sub("vegane-aufstriche", "Vegane Aufstriche"), sub("pflanzliche-desserts", "Pflanzliche Desserts")]),
    CatalogCategory(slug="vorrat", name="Vorrat & verpackt", description="Nudeln, Reis, Konserven, Snacks", icon="package", subcategories=[sub("nudeln", "Nudeln"), sub("reis", "Reis"), sub("konserven", "Konserven"), sub("muesli", "Müsli"), sub("suessigkeiten", "Süßigkeiten"), sub("snacks", "Snacks"), sub("saucen", "Saucen"), sub("gewuerze", "Gewürze")]),
    CatalogCategory(slug="haushalt", name="Haushalt", description="Reinigung, Papier und Wäsche", icon="spray-can", subcategories=[sub("waschmittel", "Waschmittel"), sub("reiniger", "Reiniger"), sub("spuelmittel", "Spülmittel"), sub("papierwaren", "Papierwaren"), sub("muellbeutel", "Müllbeutel")]),
    CatalogCategory(slug="drogerie", name="Drogerie", description="Körperpflege, Hygiene und Kosmetik", icon="sparkles", subcategories=[sub("shampoo", "Shampoo"), sub("duschgel", "Duschgel"), sub("zahnpflege", "Zahnpasta"), sub("deodorant", "Deodorant"), sub("hautpflege", "Hautpflege"), sub("hygiene", "Hygieneartikel")]),
]

BASIC_ASSORTMENT: dict[str, list[tuple[str, str]]] = {
    "aepfel": [("Apfel Gala", "1 kg"), ("Apfel Braeburn", "1 kg"), ("Apfel Elstar", "1 kg"), ("Apfel Granny Smith", "1 kg"), ("Apfel Golden Delicious", "1 kg")],
    "bananen": [("Banane", "1 kg"), ("Bio Banane", "1 kg"), ("Kochbanane", "1 Stück")],
    "beeren": [("Erdbeeren", "500 g"), ("Himbeeren", "250 g"), ("Heidelbeeren", "250 g"), ("Brombeeren", "250 g"), ("Johannisbeeren", "250 g")],
    "zitrusfruechte": [("Orange", "1 kg"), ("Mandarine", "1 kg"), ("Zitrone", "500 g"), ("Limette", "3 Stück"), ("Grapefruit", "1 Stück")],
    "trauben": [("Weintrauben hell", "500 g"), ("Weintrauben rot", "500 g"), ("Kernlose Trauben", "500 g")],
    "birnen": [("Birne Conference", "1 kg"), ("Birne Williams", "1 kg"), ("Nashi-Birne", "1 Stück")],
    "steinobst": [("Pfirsich", "1 kg"), ("Nektarine", "1 kg"), ("Pflaume", "1 kg"), ("Aprikose", "500 g"), ("Kirschen", "500 g")],
    "tropenfruechte": [("Ananas", "1 Stück"), ("Mango", "1 Stück"), ("Kiwi", "6 Stück"), ("Papaya", "1 Stück"), ("Granatapfel", "1 Stück"), ("Passionsfrucht", "3 Stück")],
    "melonen": [("Wassermelone", "1 Stück"), ("Honigmelone", "1 Stück"), ("Cantaloupe-Melone", "1 Stück")],
    "tomaten": [("Rispentomaten", "1 kg"), ("Cherrytomaten", "500 g"), ("Roma-Tomaten", "1 kg"), ("Fleischtomate", "1 kg")],
    "gurken": [("Salatgurke", "1 Stück"), ("Minigurken", "500 g"), ("Einlegegurken", "1 kg")],
    "paprika": [("Paprika rot", "500 g"), ("Paprika gelb", "500 g"), ("Paprika grün", "500 g"), ("Spitzpaprika", "500 g")],
    "kartoffeln": [("Speisekartoffeln festkochend", "2,5 kg"), ("Speisekartoffeln mehlig", "2,5 kg"), ("Frühkartoffeln", "1 kg"), ("Süßkartoffeln", "1 kg")],
    "zwiebeln": [("Zwiebeln gelb", "1 kg"), ("Zwiebeln rot", "500 g"), ("Frühlingszwiebeln", "1 Bund"), ("Schalotten", "250 g"), ("Knoblauch", "200 g")],
    "wurzelgemuese": [("Karotten", "1 kg"), ("Pastinaken", "500 g"), ("Rote Bete", "500 g"), ("Knollensellerie", "1 Stück"), ("Ingwer", "200 g"), ("Radieschen", "1 Bund")],
    "salate": [("Eisbergsalat", "1 Stück"), ("Kopfsalat", "1 Stück"), ("Römersalat", "1 Stück"), ("Feldsalat", "150 g"), ("Rucola", "125 g"), ("Babyspinat", "200 g")],
    "kohl": [("Brokkoli", "500 g"), ("Blumenkohl", "1 Stück"), ("Weißkohl", "1 Stück"), ("Rotkohl", "1 Stück"), ("Rosenkohl", "500 g"), ("Kohlrabi", "1 Stück")],
    "pilze": [("Champignons weiß", "400 g"), ("Champignons braun", "400 g"), ("Austernpilze", "250 g"), ("Kräuterseitlinge", "250 g")],
    "kraeuter": [("Petersilie", "1 Bund"), ("Schnittlauch", "1 Bund"), ("Basilikum", "1 Topf"), ("Koriander", "1 Bund"), ("Dill", "1 Bund"), ("Minze", "1 Topf")],
    "brot": [("Mischbrot", "750 g"), ("Vollkornbrot", "500 g"), ("Bauernbrot", "1 kg"), ("Roggenbrot", "750 g"), ("Baguette", "250 g")],
    "broetchen": [("Kaiserbrötchen", "1 Stück"), ("Vollkornbrötchen", "1 Stück"), ("Laugenbrötchen", "1 Stück"), ("Mehrkornbrötchen", "1 Stück")],
    "gebaeck": [("Croissant", "1 Stück"), ("Laugenbrezel", "1 Stück"), ("Rosinenschnecke", "1 Stück"), ("Schokobrötchen", "1 Stück")],
    "rind": [("Rindersteak", "300 g"), ("Rindergulasch", "500 g"), ("Rinderrouladen", "500 g"), ("Suppenfleisch vom Rind", "500 g")],
    "schwein": [("Schweineschnitzel", "500 g"), ("Schweinefilet", "500 g"), ("Schweinekotelett", "500 g"), ("Schweinegulasch", "500 g")],
    "gefluegel": [("Hähnchenbrustfilet", "500 g"), ("Hähnchenschenkel", "1 kg"), ("Putenbrust", "500 g"), ("Ganzes Hähnchen", "1 Stück")],
    "hackfleisch": [("Rinderhackfleisch", "500 g"), ("Gemischtes Hackfleisch", "500 g"), ("Geflügelhackfleisch", "400 g")],
    "lachs": [("Lachsfilet", "250 g"), ("Räucherlachs", "200 g"), ("Lachssteak", "300 g")],
    "weissfisch": [("Kabeljaufilet", "300 g"), ("Seelachsfilet", "400 g"), ("Forelle", "1 Stück"), ("Dorade", "1 Stück")],
    "thunfisch": [("Thunfischsteak", "250 g"), ("Frischer Thunfisch", "300 g")],
    "garnelen": [("Riesengarnelen", "250 g"), ("Garnelen gekocht", "200 g")],
    "muscheln": [("Miesmuscheln", "1 kg"), ("Jakobsmuscheln", "200 g")],
}


CATEGORY_BY_SLUG = {category.slug: category for category in CATEGORIES}
SUBCATEGORY_TO_GROUP = {
    subcategory.slug: category.slug
    for category in CATEGORIES
    for subcategory in category.subcategories
}
SEARCH_TERM_BY_SLUG = {
    category.slug: category.name
    for category in CATEGORIES
} | {
    subcategory.slug: subcategory.search_term
    for category in CATEGORIES
    for subcategory in category.subcategories
}

# Open-Facts-Kataloge sind weltweit gepflegt; englische Taxonomiebegriffe liefern
# über Ländergrenzen hinweg deutlich vollständigere Treffer als nur deutsche Namen.
SEARCH_TERM_BY_SLUG.update({
    "obst": "fruits", "aepfel": "apples", "bananen": "bananas", "beeren": "berries",
    "zitrusfruechte": "citrus fruits", "trauben": "grapes", "birnen": "pears",
    "steinobst": "stone fruits", "tropenfruechte": "tropical fruits", "melonen": "melons",
    "gemuese": "vegetables", "tomaten": "tomatoes", "gurken": "cucumbers", "paprika": "peppers",
    "kartoffeln": "potatoes", "zwiebeln": "onions", "wurzelgemuese": "root vegetables",
    "salate": "salads", "kohl": "cabbages", "pilze": "mushrooms", "kraeuter": "herbs",
    "getraenke": "beverages", "wasser": "water", "saefte": "fruit juices", "limonaden": "soft drinks",
    "energy": "energy drinks", "kaffee": "coffee", "tee": "tea", "bier": "beer", "wein": "wine",
    "pflanzendrinks": "plant based drinks", "milchprodukte": "dairy products", "milch": "milk",
    "joghurt": "yogurts", "kaese": "cheeses", "butter": "butter", "sahne": "cream", "eier": "eggs",
    "tiefkuehl": "frozen foods", "pizza": "pizzas", "tiefkuehlgemuese": "frozen vegetables",
    "eis": "ice creams", "tiefkuehlgerichte": "frozen meals", "tiefkuehlfisch": "frozen fish",
    "backwaren": "bakery products", "brot": "breads", "broetchen": "bread rolls", "gebaeck": "pastries",
    "kuchen": "cakes", "toast": "toast breads", "fleisch": "meats", "rind": "beef", "schwein": "pork",
    "gefluegel": "poultry", "hackfleisch": "minced meat", "wurst": "sausages",
    "fisch": "fish and seafood", "lachs": "salmon", "weissfisch": "white fish", "thunfisch": "tuna",
    "garnelen": "shrimps", "muscheln": "mussels", "vegan": "vegan foods", "tofu": "tofu",
    "fleischersatz": "meat substitutes", "vegane-aufstriche": "vegan spreads",
    "pflanzliche-desserts": "plant based desserts", "vorrat": "packaged foods", "nudeln": "pastas",
    "reis": "rices", "konserven": "canned foods", "muesli": "mueslis", "suessigkeiten": "candies",
    "snacks": "snacks", "saucen": "sauces", "gewuerze": "spices", "haushalt": "household products",
    "waschmittel": "laundry detergents", "reiniger": "cleaning products", "spuelmittel": "dishwashing products",
    "papierwaren": "paper products", "muellbeutel": "garbage bags", "drogerie": "personal care products",
    "shampoo": "shampoos", "duschgel": "shower gels", "zahnpflege": "toothpastes",
    "deodorant": "deodorants", "hautpflege": "skin care products", "hygiene": "hygiene products",
})


def normalize(value: str) -> str:
    text = unicodedata.normalize("NFKD", value.casefold())
    return "".join(character for character in text if not unicodedata.combining(character))


def slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", normalize(value)).strip("-")


def basic_catalog_products(
    query: str,
    category_slug: str | None,
    country_code: str,
    city: str,
    stores: list[str],
    page: int,
    page_size: int,
) -> tuple[list[Product], int]:
    selected_subcategories: set[str]
    if category_slug in CATEGORY_BY_SLUG:
        selected_subcategories = {subcategory.slug for subcategory in CATEGORY_BY_SLUG[category_slug].subcategories}
    elif category_slug in SUBCATEGORY_TO_GROUP:
        selected_subcategories = {category_slug}
    else:
        selected_subcategories = set(BASIC_ASSORTMENT)

    needle = normalize(query)
    matches: list[tuple[str, str, str]] = []
    for subcategory_slug, items in BASIC_ASSORTMENT.items():
        if subcategory_slug not in selected_subcategories:
            continue
        for name, package_size in items:
            if category_slug or not needle or needle in normalize(name) or needle in normalize(SEARCH_TERM_BY_SLUG.get(subcategory_slug, "")):
                matches.append((subcategory_slug, name, package_size))

    start = (page - 1) * page_size
    selected = matches[start:start + page_size]
    products: list[Product] = []
    for subcategory_slug, name, package_size in selected:
        group_slug = SUBCATEGORY_TO_GROUP[subcategory_slug]
        group = CATEGORY_BY_SLUG[group_slug]
        product_id = f"basic-{slugify(name)}"
        products.append(
            Product(
                id=product_id,
                name=name,
                brand="Frisches Grundsortiment",
                category=group.name,
                package_size=package_size,
                image_url=CATEGORY_IMAGES[group_slug],
                data_source="MarktFuchs Grundsortiment · Demo",
                keywords=[name, group.name, SEARCH_TERM_BY_SLUG[subcategory_slug]],
                offers=demo_branch_offers(product_id, package_size, country_code, city, stores),
            )
        )
    return products, len(matches)