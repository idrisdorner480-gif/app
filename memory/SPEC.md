# MarktFuchs MVP

## Was die App macht
MarktFuchs vergleicht lokale Demo-Angebote von REWE, EDEKA, LIDL, ALDI Süd, Penny und Kaufland. Nutzer suchen nach Produktnamen, Marken, Stichwörtern oder kleinen Schreibfehlern und sehen Produktbild, günstigsten Preis, Preis pro Einheit, Markt und Entfernung.

## Datenmodell
- `Product`: id, name, brand, category, package_size, image_url, keywords, offers
- `StoreOffer`: store, price, unit_price, distance_km, available, discount_percent
- `ProductSearchResponse`: query, corrected_query, results, total, data_source

## Kernflüsse
1. Suche über `GET /api/products/search?q=...`.
2. Fuzzy-/Synonym-Suche findet z. B. `piza`, `red bul`, `nutela`, `milx` und `apfel`.
3. Ergebnisansicht wechselt zwischen Karten und kompakter Vergleichstabelle.
4. Produkte werden lokal in einer Merkliste gespeichert; Sonner bestätigt das Hinzufügen/Entfernen.

## Auth / Rollen
Keine Authentifizierung im MVP.

## Datenstatus
Die Angebote sind REALISTISCHE DEMO-DATEN im Backend. LIVE-HÄNDLERDATEN sind noch NICHT angebunden; dafür fehlen konkrete Händlerquellen, API-Verträge und Zugänge.