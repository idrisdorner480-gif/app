# MarktFuchs MVP

## Was die App macht
MarktFuchs startet mit einer Sprachwahl in derselben durchsuchbaren Listenstruktur wie die anschließende weltweite Länderauswahl. Die Standortschritte sind auf Deutsch, Englisch, Französisch, Italienisch, Spanisch, Türkisch, Niederländisch, Polnisch und Portugiesisch verfügbar. Jedes Land erscheint mit Flagge, lokalem Namen und englischem Namen. Danach wird eine Stadt des Landes gewählt. Erst dann vergleicht die App lokale Demo-Angebote der in dieser Region verfügbaren Märkte.

## Datenmodell
- `Product`: id, name, brand, category, package_size, image_url, keywords, offers
- `StoreOffer`: store, country_code, price, unit_price, distance_km, available, discount_percent
- `ProductSearchResponse`: query, corrected_query, results, total, data_source
- `Country`: code, local_name, english_name, flag_url
- `City`: id, name, population
- `RegionMarkets`: country_code, city, stores, data_source

## Kernflüsse
1. Länder über `GET /api/locations/countries`, danach Städte über `GET /api/locations/cities?country=DE` auswählen.
1. Vor der Länderwahl eine Sprache suchen und auswählen; die Sprache kann später im Kopfbereich erneut geändert werden.
2. Regionale Märkte über `GET /api/locations/markets?country=DE&city=Berlin` bestimmen.
3. Suche über `GET /api/products/search?q=...&country=DE&city=Berlin`; Angebote werden serverseitig auf die regional verfügbaren Märkte begrenzt.
4. Fuzzy-/Synonym-Suche findet z. B. `piza`, `red bul`, `nutela`, `milx` und `apfel`.
5. Ergebnisansicht wechselt zwischen Karten und kompakter Vergleichstabelle.
6. Produkte werden lokal in einer Merkliste gespeichert; Sonner bestätigt das Hinzufügen/Entfernen.
7. Österreichische Regionen zeigen eigene Demo-Angebote von SPAR, BILLA, MPREIS, BILLA PLUS, HOFER, INTERSPAR, EUROSPAR, LIDL und Penny; Stadt-Overrides berücksichtigen die tatsächliche regionale Verfügbarkeit (z. B. MPREIS in Innsbruck).

## Auth / Rollen
Keine Authentifizierung im MVP.

## Datenstatus
Länder- und Städtestammdaten werden schlüsselfrei über countries.dev geladen und besitzen lokale Fallbacks. Das regionale Marktregister enthält große Ketten für zahlreiche Länder; eigene Produktpreise sind derzeit für Deutschland und Österreich gepflegt. Die Angebote und regionalen Marktfreigaben sind REALISTISCHE DEMO-DATEN im Backend. LIVE-HÄNDLERDATEN sind noch NICHT angebunden; dafür fehlen konkrete Händlerquellen, API-Verträge und Zugänge.