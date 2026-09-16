import { useMemo, useState } from "react";
import type { FormEvent } from "react";
import { useQuery } from "@tanstack/react-query";
import {
  ArrowLeft,
  ArrowDownUp,
  Check,
  ChevronRight,
  Globe2,
  Heart,
  LayoutGrid,
  Languages,
  List,
  MapPin,
  Search,
  ShoppingBasket,
  Sparkles,
  Store,
  Tag,
  X,
} from "lucide-react";
import { toast } from "sonner";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { fetchCities, fetchCountries, type Country, type SelectedLocation } from "@/lib/locations";
import { LANGUAGES, LOCATION_COPY, type LanguageCode } from "@/lib/languages";
import { fetchCatalogCategories } from "@/lib/catalog";
import { fetchProducts, type Product, type StoreOffer } from "@/lib/products";

type SortOption = "price" | "unit" | "distance" | "discount";
type ViewMode = "cards" | "table";

const POPULAR_SEARCHES = ["Pizza", "Red Bull 24er", "Kaffee", "Milch 1L", "Nutella", "Äpfel"];
const CATEGORY_SYMBOLS: Record<string, string> = {
  obst: "🍎", gemuese: "🥕", getraenke: "🥤", milchprodukte: "🥛", tiefkuehl: "❄️", backwaren: "🥐",
  fleisch: "🥩", fisch: "🐟", vegan: "🌿", vorrat: "📦", haushalt: "🧽", drogerie: "🧴",
};
const STORE_STYLES: Record<string, string> = {
  REWE: "bg-[#e2001a] text-white",
  EDEKA: "bg-[#005ca9] text-[#ffed00]",
  LIDL: "bg-[#0050aa] text-[#fff000]",
  "ALDI Süd": "bg-[#00205b] text-[#00a3e0]",
  Penny: "bg-[#cd1318] text-white",
  Kaufland: "bg-[#e2001a] text-white",
  SPAR: "bg-[#15803d] text-white",
  BILLA: "bg-[#facc15] text-red-700",
  MPREIS: "bg-[#e11d48] text-white",
  "BILLA PLUS": "bg-[#facc15] text-red-700",
  HOFER: "bg-[#2563eb] text-white",
  INTERSPAR: "bg-[#15803d] text-white",
  EUROSPAR: "bg-[#166534] text-white",
};

const formatEuro = (value: number) =>
  value.toLocaleString("de-DE", { style: "currency", currency: "EUR" });

const lowestOffer = (product: Product) => {
  if (!product.offers.length) return null;
  const availableOffers = product.offers.filter((offer) => offer.available);
  const candidates = availableOffers.length ? availableOffers : product.offers;
  return candidates.reduce((lowest, current) => (current.price < lowest.price ? current : lowest));
};

const closestOffer = (product: Product) => product.offers.length
  ? product.offers.reduce((closest, current) => current.distance_km < closest.distance_km ? current : closest)
  : null;

function StoreMark({ store }: { store: string }) {
  return (
    <span
      className={`inline-flex h-7 min-w-7 items-center justify-center rounded-lg px-2 text-[10px] font-black tracking-tight shadow-sm ${STORE_STYLES[store] ?? "bg-slate-800 text-white"}`}
    >
      {store === "ALDI Süd" ? "ALDI" : store}
    </span>
  );
}

function OfferRow({ productId, offer, isBest }: { productId: string; offer: StoreOffer; isBest: boolean }) {
  const statusStyle = offer.stock_status === "verfügbar"
    ? "bg-emerald-100 text-emerald-700"
    : offer.stock_status === "knapp"
      ? "bg-amber-100 text-amber-700"
      : "bg-slate-200 text-slate-500";
  return (
    <div
      className={`flex items-center gap-3 rounded-xl px-3 py-2.5 ${isBest ? "bg-emerald-50 ring-1 ring-emerald-200" : "bg-slate-50"} ${!offer.available ? "opacity-65" : ""}`}
      data-testid={`store-offer-item-${productId}-${offer.branch_id}`}
    >
      <StoreMark store={offer.store} />
      <div className="min-w-0 flex-1">
        <p className="truncate text-xs font-semibold text-slate-700" data-testid={`branch-name-${offer.branch_id}`}>{offer.branch_name || offer.store}</p>
        <p className="truncate text-[10px] text-slate-400" data-testid={`branch-address-${offer.branch_id}`}>{offer.address}</p>
        <p className="mt-1 flex items-center gap-1 text-[11px] text-slate-400"><MapPin className="h-3 w-3" /> {offer.distance_km.toFixed(1).replace(".", ",")} km</p>
      </div>
      <div className="text-right">
        <span className={`rounded-full px-2 py-0.5 text-[9px] font-bold ${statusStyle}`} data-testid={`stock-status-${offer.branch_id}`}>{offer.stock_status}</span>
        <p className={`mt-1 text-sm font-extrabold ${isBest ? "text-emerald-700" : "text-slate-800"}`}>
          {formatEuro(offer.price)}
        </p>
        <p className="text-[10px] font-semibold text-slate-400">
          {formatEuro(offer.unit_price)} / Einheit
        </p>
      </div>
      {isBest ? <Check className="h-4 w-4 text-emerald-600" /> : null}
    </div>
  );
}

function ProductCard({ product, isFavorite, onToggleFavorite }: { product: Product; isFavorite: boolean; onToggleFavorite: () => void }) {
  const cheapest = lowestOffer(product);
  const nearest = closestOffer(product);
  return (
    <Card className="group overflow-hidden rounded-[1.35rem] border-slate-200/80 bg-white shadow-[0_8px_30px_rgba(15,23,42,0.05)] transition duration-200 ease-out hover:-translate-y-1 hover:shadow-[0_18px_40px_rgba(15,23,42,0.1)]" data-testid={`product-card-item-${product.id}`}>
      <div className="relative h-48 overflow-hidden bg-slate-100">
        <img src={product.image_url} alt={product.name} className="h-full w-full object-cover transition duration-500 group-hover:scale-105" data-testid={`product-image-${product.id}`} />
        <div className="absolute inset-x-3 top-3 flex items-start justify-between">
          <Badge className="border-0 bg-white/90 text-slate-700 shadow-sm backdrop-blur-sm">{product.category}</Badge>
          <button
            type="button"
            onClick={onToggleFavorite}
            aria-label={isFavorite ? `${product.name} aus Merkliste entfernen` : `${product.name} merken`}
            className={`flex h-9 w-9 items-center justify-center rounded-full bg-white/90 shadow-sm backdrop-blur-sm transition duration-200 hover:scale-110 ${isFavorite ? "text-rose-500" : "text-slate-500 hover:text-rose-500"}`}
            data-testid={`favorite-toggle-btn-${product.id}`}
          >
            <Heart className={`h-[18px] w-[18px] ${isFavorite ? "fill-current" : ""}`} />
          </button>
        </div>
        {cheapest && cheapest.discount_percent > 0 ? (
            <span className="absolute bottom-3 left-3 rounded-full bg-red-500 px-2.5 py-1 text-[11px] font-bold text-white shadow-sm" data-testid={`discount-badge-${product.id}`}>
            -{cheapest.discount_percent}% Angebot
          </span>
        ) : null}
      </div>
      <CardContent className="p-5">
        <div className="mb-4">
          <div className="mb-1 flex items-center justify-between gap-2"><p className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-400">{product.brand}</p><span className="rounded-full bg-slate-100 px-2 py-1 text-[9px] font-bold text-slate-500" data-testid={`product-source-${product.id}`}>{product.data_source}</span></div>
          <h3 className="min-h-12 text-lg font-bold leading-tight tracking-tight text-slate-900" data-testid={`product-title-${product.id}`}>{product.name}</h3>
          <p className="mt-1 text-sm text-slate-500">{product.package_size}{product.barcode ? <span className="ml-2 text-[10px] text-slate-400">EAN {product.barcode}</span> : null}</p>
        </div>
        {cheapest && nearest ? <div className="mb-4 flex items-end justify-between border-b border-slate-100 pb-4">
          <div>
            <p className="text-[11px] font-bold uppercase tracking-[0.12em] text-emerald-700">Bester Preis</p>
            <p className="text-3xl font-black tracking-tight text-emerald-600" data-testid={`best-price-badge-${product.id}`}>{formatEuro(cheapest.price)}</p>
            <p className="text-xs font-semibold text-slate-500">{formatEuro(cheapest.unit_price)} / Einheit</p>
          </div>
          <div className="text-right text-xs text-slate-500">
            <p className="mb-1 flex items-center justify-end gap-1"><MapPin className="h-3.5 w-3.5 text-emerald-600" />{nearest.distance_km.toFixed(1).replace(".", ",")} km entfernt</p>
            <p className="font-semibold text-slate-700">{product.offers.length} Filialen geprüft</p>
          </div>
        </div> : <div className="mb-4 rounded-xl border border-dashed border-slate-200 bg-slate-50 p-3 text-sm text-slate-500" data-testid={`product-no-branches-${product.id}`}>Produkt im weltweiten Katalog gefunden – für diese Region sind noch keine Demo-Filialen hinterlegt.</div>}
        <div className="space-y-2">
          {product.offers.slice().sort((a, b) => a.price - b.price).map((offer) => (
            <OfferRow key={`${product.id}-${offer.branch_id}`} productId={product.id} offer={offer} isBest={offer.branch_id === cheapest?.branch_id} />
          ))}
        </div>
      </CardContent>
    </Card>
  );
}

function ComparisonTable({ products, favoriteIds, onToggleFavorite }: { products: Product[]; favoriteIds: Set<string>; onToggleFavorite: (id: string) => void }) {
  return (
    <div className="overflow-hidden rounded-[1.35rem] border border-slate-200 bg-white shadow-[0_8px_30px_rgba(15,23,42,0.05)]" data-testid="price-comparison-table">
      <div className="overflow-x-auto">
        <table className="w-full min-w-[760px] text-left">
          <thead className="bg-slate-50 text-[11px] uppercase tracking-[0.14em] text-slate-500">
            <tr>
              <th className="px-5 py-4 font-bold">Produkt</th>
              <th className="px-4 py-4 font-bold">Günstigster Preis</th>
              <th className="px-4 py-4 font-bold">Stückpreis</th>
              <th className="px-4 py-4 font-bold">Nächste Filiale</th>
              <th className="px-4 py-4 font-bold">Angebote</th>
              <th className="px-4 py-4" />
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {products.map((product) => {
              const cheapest = lowestOffer(product);
              const nearest = closestOffer(product);
              return (
                <tr key={product.id} className="group transition hover:bg-emerald-50/40" data-testid={`table-row-product-${product.id}`}>
                  <td className="px-5 py-4">
                    <div className="flex items-center gap-3">
                      <img src={product.image_url} alt="" className="h-12 w-12 rounded-xl object-cover" />
                      <div><p className="font-bold text-slate-900">{product.name}</p><p className="text-xs text-slate-500">{product.package_size}</p></div>
                    </div>
                  </td>
                  <td className="px-4 py-4">{cheapest ? <div className="flex items-center gap-2"><StoreMark store={cheapest.store} /><span className="font-extrabold text-emerald-700" data-testid={`table-cell-cheapest-highlight-${product.id}`}>{formatEuro(cheapest.price)}</span></div> : <span className="text-xs text-slate-400">Keine Filiale</span>}</td>
                  <td className="px-4 py-4">{cheapest ? <span className="rounded-full bg-slate-100 px-2 py-1 text-xs font-bold text-slate-600">{formatEuro(cheapest.unit_price)} / Einheit</span> : "–"}</td>
                  <td className="px-4 py-4 text-sm font-semibold text-slate-600">{nearest ? <span className="flex items-center gap-1"><MapPin className="h-3.5 w-3.5 text-emerald-600" />{nearest.distance_km.toFixed(1).replace(".", ",")} km</span> : "–"}</td>
                  <td className="px-4 py-4"><div className="flex -space-x-1">{product.offers.map((offer) => <StoreMark key={offer.branch_id} store={offer.store} />)}</div></td>
                  <td className="px-4 py-4"><button type="button" onClick={() => onToggleFavorite(product.id)} className={`rounded-full p-2 transition hover:bg-rose-50 ${favoriteIds.has(product.id) ? "text-rose-500" : "text-slate-400 hover:text-rose-500"}`} data-testid={`favorite-toggle-table-btn-${product.id}`}><Heart className={`h-4 w-4 ${favoriteIds.has(product.id) ? "fill-current" : ""}`} /></button></td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function LocationGate({ languageCode, onLanguageChange, onComplete }: { languageCode: LanguageCode; onLanguageChange: (language: LanguageCode) => void; onComplete: (location: SelectedLocation) => void }) {
  const [stage, setStage] = useState<"language" | "country" | "city">("language");
  const [languageSearch, setLanguageSearch] = useState("");
  const [countrySearch, setCountrySearch] = useState("");
  const [citySearch, setCitySearch] = useState("");
  const [selectedCountry, setSelectedCountry] = useState<Country | null>(null);
  const countriesQuery = useQuery({ queryKey: ["locations", "countries"], queryFn: fetchCountries, retry: 1 });
  const citiesQuery = useQuery({
    queryKey: ["locations", "cities", selectedCountry?.code],
    queryFn: () => fetchCities(selectedCountry?.code ?? ""),
    enabled: Boolean(selectedCountry),
    retry: 1,
  });
  const copy = LOCATION_COPY[languageCode];

  const languages = useMemo(() => {
    const needle = languageSearch.trim().toLocaleLowerCase();
    return LANGUAGES.filter((language) =>
      !needle || `${language.native_name} ${language.english_name}`.toLocaleLowerCase().includes(needle),
    );
  }, [languageSearch]);

  const countries = useMemo(() => {
    const needle = countrySearch.trim().toLocaleLowerCase();
    return (countriesQuery.data ?? []).filter((country) =>
      !needle || `${country.local_name} ${country.english_name}`.toLocaleLowerCase().includes(needle),
    );
  }, [countriesQuery.data, countrySearch]);

  const cities = useMemo(() => {
    const needle = citySearch.trim().toLocaleLowerCase();
    return (citiesQuery.data ?? []).filter((city) =>
      !needle || city.name.toLocaleLowerCase().includes(needle),
    );
  }, [citiesQuery.data, citySearch]);

  return (
    <div className="fixed inset-0 z-[70] overflow-y-auto bg-[#f6f8f7]" data-testid="location-gate">
      <div className="pointer-events-none fixed -left-20 -top-20 h-96 w-96 rounded-full bg-emerald-200/35 blur-3xl" />
      <div className="pointer-events-none fixed -bottom-24 right-0 h-96 w-96 rounded-full bg-lime-100/60 blur-3xl" />
      <div className="relative mx-auto flex min-h-svh max-w-5xl flex-col px-5 py-8 sm:px-8 lg:py-12">
        <div className="mb-8 flex items-center gap-3" data-testid="location-brand">
          <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-emerald-600 text-white shadow-[0_8px_18px_rgba(22,163,74,0.25)]"><ShoppingBasket className="h-5 w-5" /></div>
          <p className="text-xl font-black tracking-tight text-slate-900">Markt<span className="text-emerald-600">Fuchs</span></p>
        </div>

        <div className="mx-auto w-full max-w-3xl flex-1">
          {stage === "language" ? (
            <>
              <div className="mb-7">
                <div className="mb-3 inline-flex items-center gap-2 rounded-full bg-emerald-100 px-3 py-1.5 text-xs font-bold text-emerald-700"><Languages className="h-3.5 w-3.5" /> {copy.languageStep}</div>
                <h1 className="text-3xl font-black tracking-[-0.035em] text-slate-950 sm:text-5xl" data-testid="language-selection-title">{copy.languageTitle}</h1>
                <p className="mt-3 text-base text-slate-500">{copy.languageSubtitle}</p>
              </div>
              <div className="sticky top-4 z-10 mb-4 flex items-center rounded-2xl border border-slate-200 bg-white/95 px-4 shadow-[0_10px_30px_rgba(15,23,42,0.08)] backdrop-blur-xl focus-within:border-emerald-400 focus-within:ring-4 focus-within:ring-emerald-100"><Search className="h-4 w-4 shrink-0 text-emerald-600" /><Input value={languageSearch} onChange={(event) => setLanguageSearch(event.target.value)} placeholder={copy.searchLanguage} className="h-14 border-0 bg-transparent shadow-none focus-visible:ring-0" autoFocus data-testid="language-search-input" /></div>
              <div className="overflow-hidden rounded-3xl border border-slate-200/80 bg-white shadow-[0_14px_45px_rgba(15,23,42,0.07)]" data-testid="language-list"><div className="max-h-[52vh] divide-y divide-slate-100 overflow-y-auto">{languages.map((language) => (
                <button type="button" key={language.code} onClick={() => { onLanguageChange(language.code); setStage("country"); }} className="flex w-full items-center gap-4 px-5 py-3.5 text-left transition duration-150 hover:bg-emerald-50 focus:bg-emerald-50" data-testid={`language-option-${language.code}`}><span className="flex h-9 w-11 items-center justify-center rounded-lg bg-slate-900 text-xs font-black text-white">{language.symbol}</span><span className="min-w-0 flex-1 font-bold text-slate-800">{language.native_name} <span className="font-medium text-slate-400">({language.english_name})</span></span><ChevronRight className="h-4 w-4 text-slate-300" /></button>
              ))}{languages.length === 0 ? <div className="p-8 text-center text-sm text-slate-500">{copy.noResult}</div> : null}</div></div>
            </>
          ) : stage === "country" ? (
            <>
              <button type="button" onClick={() => setStage("language")} className="mb-6 inline-flex items-center gap-2 rounded-xl px-3 py-2 text-sm font-bold text-slate-500 transition hover:bg-white hover:text-emerald-700" data-testid="language-back-button"><ArrowLeft className="h-4 w-4" /> {copy.changeLanguage}</button>
              <div className="mb-7">
                <div className="mb-3 inline-flex items-center gap-2 rounded-full bg-emerald-100 px-3 py-1.5 text-xs font-bold text-emerald-700"><Globe2 className="h-3.5 w-3.5" /> {copy.countryStep}</div>
                <h1 className="text-3xl font-black tracking-[-0.035em] text-slate-950 sm:text-5xl" data-testid="country-selection-title">{copy.countryTitle}</h1>
                <p className="mt-3 text-base text-slate-500">{copy.countrySubtitle}</p>
              </div>
              <div className="sticky top-4 z-10 mb-4 flex items-center rounded-2xl border border-slate-200 bg-white/95 px-4 shadow-[0_10px_30px_rgba(15,23,42,0.08)] backdrop-blur-xl focus-within:border-emerald-400 focus-within:ring-4 focus-within:ring-emerald-100">
                <Search className="h-4 w-4 shrink-0 text-emerald-600" />
                <Input value={countrySearch} onChange={(event) => setCountrySearch(event.target.value)} placeholder={copy.searchCountry} className="h-14 border-0 bg-transparent shadow-none focus-visible:ring-0" autoFocus data-testid="country-search-input" />
              </div>
              <div className="overflow-hidden rounded-3xl border border-slate-200/80 bg-white shadow-[0_14px_45px_rgba(15,23,42,0.07)]" data-testid="country-list">
                {countriesQuery.isLoading ? <div className="p-8 text-center text-sm font-semibold text-slate-500">{copy.loading}</div> : countriesQuery.isError ? <div className="p-8 text-center"><p className="font-bold text-amber-800">{copy.unavailable}</p></div> : countries.length ? <div className="max-h-[52vh] divide-y divide-slate-100 overflow-y-auto">{countries.map((country) => (
                  <button type="button" key={country.code} onClick={() => { setSelectedCountry(country); setCitySearch(""); setStage("city"); }} className="flex w-full items-center gap-4 px-5 py-3.5 text-left transition duration-150 hover:bg-emerald-50 focus:bg-emerald-50" data-testid={`country-option-${country.code.toLowerCase()}`}>
                    <img src={country.flag_url} alt={`Flagge ${country.local_name}`} className="h-7 w-10 rounded-md border border-slate-200 object-cover shadow-sm" data-testid={`country-flag-${country.code.toLowerCase()}`} />
                    <span className="min-w-0 flex-1 font-bold text-slate-800" data-testid={`country-name-${country.code.toLowerCase()}`}>{country.local_name} <span className="font-medium text-slate-400">({country.english_name})</span></span>
                    <ChevronRight className="h-4 w-4 text-slate-300" />
                  </button>
                ))}</div> : <div className="p-8 text-center text-sm text-slate-500">{copy.noResult}</div>}
              </div>
            </>
          ) : selectedCountry ? (
            <>
              <button type="button" onClick={() => { setSelectedCountry(null); setStage("country"); }} className="mb-6 inline-flex items-center gap-2 rounded-xl px-3 py-2 text-sm font-bold text-slate-500 transition hover:bg-white hover:text-emerald-700" data-testid="country-back-button"><ArrowLeft className="h-4 w-4" /> {copy.changeCountry}</button>
              <div className="mb-7 flex items-start gap-4">
                <img src={selectedCountry.flag_url} alt={`Flagge ${selectedCountry.local_name}`} className="mt-1 h-10 w-14 rounded-lg border border-slate-200 object-cover shadow-sm" data-testid="selected-country-flag" />
                <div><div className="mb-2 inline-flex items-center gap-2 rounded-full bg-emerald-100 px-3 py-1.5 text-xs font-bold text-emerald-700"><MapPin className="h-3.5 w-3.5" /> {copy.cityStep}</div><h1 className="text-3xl font-black tracking-[-0.035em] text-slate-950 sm:text-5xl" data-testid="city-selection-title">{copy.cityTitle}</h1><p className="mt-3 text-base text-slate-500">{copy.citiesIn} {selectedCountry.local_name} ({selectedCountry.english_name})</p></div>
              </div>
              <div className="sticky top-4 z-10 mb-4 flex items-center rounded-2xl border border-slate-200 bg-white/95 px-4 shadow-[0_10px_30px_rgba(15,23,42,0.08)] backdrop-blur-xl focus-within:border-emerald-400 focus-within:ring-4 focus-within:ring-emerald-100"><Search className="h-4 w-4 shrink-0 text-emerald-600" /><Input value={citySearch} onChange={(event) => setCitySearch(event.target.value)} placeholder={copy.searchCity} className="h-14 border-0 bg-transparent shadow-none focus-visible:ring-0" autoFocus data-testid="city-search-input" /></div>
              <div className="overflow-hidden rounded-3xl border border-slate-200/80 bg-white shadow-[0_14px_45px_rgba(15,23,42,0.07)]" data-testid="city-list">
                {citiesQuery.isLoading ? <div className="p-8 text-center text-sm font-semibold text-slate-500">{copy.loading}</div> : citiesQuery.isError ? <div className="p-8 text-center"><p className="font-bold text-amber-800">{copy.unavailable}</p></div> : cities.length ? <div className="grid max-h-[52vh] grid-cols-1 gap-px overflow-y-auto bg-slate-100 sm:grid-cols-2">{cities.map((city) => (
                  <button type="button" key={city.id} onClick={() => onComplete({ country: selectedCountry, city })} className="flex items-center justify-between bg-white px-5 py-4 text-left font-bold text-slate-700 transition duration-150 hover:bg-emerald-50 hover:text-emerald-800" data-testid={`city-option-${city.id.toLowerCase().replaceAll(" ", "-")}`}><span>{city.name}</span><ChevronRight className="h-4 w-4 text-slate-300" /></button>
                ))}</div> : <div className="p-8 text-center text-sm text-slate-500">{copy.noResult}</div>}
              </div>
            </>
          ) : null}
        </div>
        <p className="mt-7 text-center text-xs text-slate-400" data-testid="location-data-source">{copy.source}</p>
      </div>
    </div>
  );
}

function Watchlist({ products, favoriteIds, onClose, onToggleFavorite }: { products: Product[]; favoriteIds: Set<string>; onClose: () => void; onToggleFavorite: (id: string) => void }) {
  const saved = products.filter((product) => favoriteIds.has(product.id));
  const savings = saved.reduce((total, product) => {
    const prices = product.offers.map((offer) => offer.price);
    return prices.length ? total + Math.max(...prices) - Math.min(...prices) : total;
  }, 0);
  return (
    <div className="fixed inset-0 z-50 bg-slate-950/20 backdrop-blur-[2px]" data-testid="watchlist-overlay">
      <aside className="absolute right-0 top-0 flex h-full w-full max-w-md flex-col bg-white shadow-2xl" data-testid="watchlist-sheet-container">
        <div className="flex items-center justify-between border-b border-slate-100 px-6 py-5"><div><p className="text-xs font-bold uppercase tracking-[0.15em] text-emerald-600">Deine Auswahl</p><h2 className="text-2xl font-black tracking-tight text-slate-900">Merkliste</h2></div><button type="button" onClick={onClose} className="rounded-full p-2 text-slate-400 transition hover:bg-slate-100 hover:text-slate-800" aria-label="Merkliste schließen" data-testid="watchlist-close-button"><X className="h-5 w-5" /></button></div>
        {saved.length > 0 ? <><div className="m-5 rounded-2xl bg-emerald-50 p-4" data-testid="watchlist-total-savings"><p className="text-xs font-bold uppercase tracking-[0.12em] text-emerald-700">Mögliches Sparpotenzial</p><p className="mt-1 text-2xl font-black text-emerald-700">bis zu {formatEuro(savings)}</p><p className="mt-1 text-xs text-emerald-700/80">wenn du Preise vergleichst</p></div><div className="flex-1 space-y-3 overflow-y-auto px-5">{saved.map((product) => { const cheapest = lowestOffer(product); return <div key={product.id} className="flex items-center gap-3 rounded-2xl border border-slate-100 p-3" data-testid={`watchlist-item-row-${product.id}`}><img src={product.image_url} alt="" className="h-14 w-14 rounded-xl object-cover" /><div className="min-w-0 flex-1"><p className="truncate text-sm font-bold text-slate-800">{product.name}</p><p className="text-xs text-slate-500">{cheapest ? `ab ${formatEuro(cheapest.price)} bei ${cheapest.store}` : "Noch keine regionale Filiale"}</p></div><button type="button" onClick={() => onToggleFavorite(product.id)} className="rounded-full p-2 text-rose-500 hover:bg-rose-50" aria-label={`${product.name} entfernen`} data-testid={`watchlist-remove-button-${product.id}`}><Heart className="h-4 w-4 fill-current" /></button></div>; })}</div></> : <div className="flex flex-1 flex-col items-center justify-center px-8 text-center"><div className="mb-4 rounded-full bg-emerald-50 p-4 text-emerald-600"><Heart className="h-7 w-7" /></div><h3 className="text-lg font-bold text-slate-800">Noch nichts gemerkt</h3><p className="mt-2 text-sm leading-relaxed text-slate-500">Speichere Produkte über das Herz, um sie hier schnell wiederzufinden.</p></div>}
        <div className="border-t border-slate-100 p-5"><Button className="w-full rounded-xl bg-emerald-600 font-bold hover:bg-emerald-700" onClick={onClose} data-testid="watchlist-done-button">Weiter vergleichen</Button></div>
      </aside>
    </div>
  );
}

export default function Home() {
  const [query, setQuery] = useState("Pizza");
  const [submittedQuery, setSubmittedQuery] = useState("Pizza");
  const [viewMode, setViewMode] = useState<ViewMode>("cards");
  const [sortBy, setSortBy] = useState<SortOption>("price");
  const [favoriteIds, setFavoriteIds] = useState<Set<string>>(new Set());
  const [watchlistOpen, setWatchlistOpen] = useState(false);
  const [location, setLocation] = useState<SelectedLocation | null>(null);
  const [locationOpen, setLocationOpen] = useState(true);
  const [languageCode, setLanguageCode] = useState<LanguageCode>("de");
  const [page, setPage] = useState(1);
  const [activeCategory, setActiveCategory] = useState<string | null>(null);
  const [selectedCategory, setSelectedCategory] = useState<string | undefined>();
  const categoriesQuery = useQuery({ queryKey: ["catalog", "categories"], queryFn: fetchCatalogCategories, retry: false });
  const { data, isLoading, isError } = useQuery({
    queryKey: ["products", submittedQuery, selectedCategory, location?.country.code, location?.city.name, page],
    queryFn: () => fetchProducts(submittedQuery, location?.country.code ?? "", location?.city.name ?? "", page, 24, selectedCategory),
    enabled: Boolean(location),
    retry: false,
  });

  const products = useMemo(() => {
    const list = [...(data?.results ?? [])];
    return list.sort((a, b) => {
      if (sortBy === "unit") return (lowestOffer(a)?.unit_price ?? Infinity) - (lowestOffer(b)?.unit_price ?? Infinity);
      if (sortBy === "distance") return (closestOffer(a)?.distance_km ?? Infinity) - (closestOffer(b)?.distance_km ?? Infinity);
      if (sortBy === "discount") return (lowestOffer(b)?.discount_percent ?? 0) - (lowestOffer(a)?.discount_percent ?? 0);
      return (lowestOffer(a)?.price ?? Infinity) - (lowestOffer(b)?.price ?? Infinity);
    });
  }, [data?.results, sortBy]);

  const toggleFavorite = (id: string) => {
    const product = data?.results.find((item) => item.id === id);
    setFavoriteIds((current) => {
      const next = new Set(current);
      const nowSaved = !next.has(id);
      if (nowSaved) next.add(id); else next.delete(id);
      if (product) toast(nowSaved ? "Zur Merkliste hinzugefügt" : "Aus Merkliste entfernt", { description: product.name });
      return next;
    });
  };

  const submitSearch = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setPage(1);
    setSelectedCategory(undefined);
    setSubmittedQuery(query.trim());
  };

  return (
    <div className="min-h-svh bg-[#f8f9fa] text-[#121826]">
      <header className="sticky top-0 z-40 border-b border-slate-200/70 bg-white/85 backdrop-blur-xl" data-testid="header-nav">
        <div className="mx-auto flex max-w-[1440px] items-center justify-between gap-5 px-5 py-4 lg:px-10">
          <div className="flex items-center gap-3"><div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-emerald-600 text-white shadow-[0_8px_18px_rgba(22,163,74,0.25)]"><ShoppingBasket className="h-5 w-5" /></div><div><p className="text-lg font-black tracking-tight text-slate-900">Markt<span className="text-emerald-600">Fuchs</span></p><p className="hidden text-[10px] font-bold uppercase tracking-[0.18em] text-slate-400 sm:block">Preise clever vergleichen</p></div></div>
          <button type="button" onClick={() => setLocationOpen(true)} className="flex items-center gap-2 rounded-full bg-slate-100 px-3 py-2 text-xs font-bold uppercase text-slate-600 transition hover:bg-emerald-50 hover:text-emerald-700" data-testid="language-change-button"><Languages className="h-3.5 w-3.5" /> {languageCode}</button>
          <button type="button" onClick={() => setLocationOpen(true)} className="hidden items-center gap-2 rounded-full bg-slate-100 px-4 py-2 text-xs font-semibold text-slate-600 transition hover:bg-emerald-50 hover:text-emerald-700 md:flex" data-testid="location-change-button"><MapPin className="h-3.5 w-3.5 text-emerald-600" /> {location ? `${location.city.name}, ${location.country.code}` : "Region wählen"} <span className="ml-1 text-slate-400">⌄</span></button>
          <button type="button" onClick={() => setWatchlistOpen(true)} className="relative flex items-center gap-2 rounded-xl px-3 py-2 text-sm font-bold text-slate-600 transition hover:bg-emerald-50 hover:text-emerald-700" data-testid="watchlist-nav-button"><Heart className="h-[18px] w-[18px]" /> <span className="hidden sm:inline">Merkliste</span>{favoriteIds.size > 0 ? <span className="flex h-5 min-w-5 items-center justify-center rounded-full bg-rose-500 px-1 text-[10px] font-black text-white">{favoriteIds.size}</span> : null}</button>
        </div>
      </header>

      <main className="mx-auto max-w-[1440px] px-5 pb-20 lg:px-10">
        <section className="relative overflow-hidden pb-10 pt-14 lg:pb-14 lg:pt-20" data-testid="search-hero-section">
          <div className="pointer-events-none absolute -right-10 -top-20 h-72 w-72 rounded-full bg-emerald-200/35 blur-3xl" /><div className="pointer-events-none absolute bottom-0 left-1/3 h-28 w-80 rounded-full bg-lime-100/50 blur-3xl" />
          <div className="relative max-w-3xl"><div className="mb-4 inline-flex items-center gap-2 rounded-full bg-emerald-100 px-3 py-1.5 text-xs font-bold text-emerald-700"><Sparkles className="h-3.5 w-3.5" /> Angebote in deiner Nähe</div><h1 className="text-4xl font-black leading-[1.05] tracking-[-0.04em] text-slate-950 sm:text-5xl lg:text-6xl">Finde den besten Preis.<br /><span className="text-emerald-600">Ganz einfach.</span></h1><p className="mt-5 max-w-xl text-base leading-relaxed text-slate-500 sm:text-lg">Suche nach Produkten, Marken oder Stichwörtern – auch kleine Tippfehler sind kein Problem.</p>
            <form onSubmit={submitSearch} className="relative mt-8 flex max-w-2xl items-center rounded-2xl border border-slate-200 bg-white p-2 shadow-[0_12px_35px_rgba(15,23,42,0.09)] focus-within:border-emerald-400 focus-within:ring-4 focus-within:ring-emerald-100" data-testid="product-search-form"><Search className="ml-3 h-5 w-5 shrink-0 text-emerald-600" /><Input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="z. B. „Red Bull 24er“ oder „Piza“" className="h-12 border-0 bg-transparent text-base shadow-none focus-visible:ring-0" data-testid="search-input-main" /><Button type="submit" className="h-12 rounded-xl bg-emerald-600 px-5 font-bold shadow-sm hover:bg-emerald-700" data-testid="search-submit-button">Suchen</Button></form>
            <div className="mt-4 flex flex-wrap items-center gap-2"><span className="mr-1 text-xs font-bold uppercase tracking-[0.12em] text-slate-400">Beliebt</span>{POPULAR_SEARCHES.map((item) => <button type="button" key={item} onClick={() => { setQuery(item); setSubmittedQuery(item); setSelectedCategory(undefined); setPage(1); }} className="rounded-full border border-slate-200 bg-white px-3 py-1.5 text-xs font-semibold text-slate-600 transition hover:-translate-y-0.5 hover:border-emerald-300 hover:text-emerald-700" data-testid={`popular-search-tag-${item.toLowerCase().replaceAll(" ", "-")}`}>{item}</button>)}</div>
          </div>
        </section>

        <section className="mb-10" data-testid="catalog-category-browser">
          <div className="mb-4 flex items-end justify-between"><div><p className="text-xs font-bold uppercase tracking-[0.14em] text-emerald-700">Komplettes Sortiment</p><h2 className="mt-1 text-2xl font-black tracking-tight text-slate-900">Nach Kategorie stöbern</h2></div><p className="hidden text-sm text-slate-500 sm:block">Von frischer Banane bis Waschmittel</p></div>
          <div className="grid grid-cols-2 gap-2 sm:grid-cols-3 lg:grid-cols-6">{(categoriesQuery.data ?? []).map((category) => <button type="button" key={category.slug} onClick={() => { setActiveCategory((current) => current === category.slug ? null : category.slug); setSelectedCategory(category.slug); setQuery(category.name); setSubmittedQuery(category.name); setPage(1); }} className={`rounded-2xl border p-3 text-left transition duration-200 hover:-translate-y-0.5 ${activeCategory === category.slug ? "border-emerald-400 bg-emerald-50 shadow-sm" : "border-slate-200 bg-white hover:border-emerald-200"}`} data-testid={`catalog-category-${category.slug}`}><span className="text-2xl">{CATEGORY_SYMBOLS[category.slug] ?? "🛒"}</span><p className="mt-2 text-sm font-black text-slate-800">{category.name}</p><p className="mt-0.5 line-clamp-1 text-[10px] text-slate-400">{category.description}</p></button>)}</div>
          {activeCategory ? <div className="mt-3 flex flex-wrap gap-2 rounded-2xl border border-emerald-100 bg-white p-4" data-testid="catalog-subcategory-list">{categoriesQuery.data?.find((category) => category.slug === activeCategory)?.subcategories.map((subcategory) => <button type="button" key={subcategory.slug} onClick={() => { setSelectedCategory(subcategory.slug); setQuery(subcategory.name); setSubmittedQuery(subcategory.search_term); setPage(1); }} className={`rounded-full px-3 py-2 text-xs font-bold transition ${selectedCategory === subcategory.slug ? "bg-emerald-600 text-white" : "bg-slate-100 text-slate-600 hover:bg-emerald-100 hover:text-emerald-800"}`} data-testid={`catalog-subcategory-${subcategory.slug}`}>{subcategory.name}</button>)}</div> : null}
        </section>

        <section aria-label="Suchergebnisse" data-testid="search-results-section">
          <div className="mb-6 flex flex-col gap-4 border-b border-slate-200 pb-5 xl:flex-row xl:items-end xl:justify-between"><div><div className="flex items-center gap-2"><h2 className="text-2xl font-black tracking-tight text-slate-900 sm:text-3xl">{submittedQuery ? `Ergebnisse für „${submittedQuery}“` : "Alle Angebote"}</h2>{data?.total ? <Badge variant="secondary" className="rounded-full bg-emerald-100 text-emerald-700">{data.total} Treffer</Badge> : null}</div>{data?.corrected_query ? <button type="button" onClick={() => { setQuery(data.corrected_query ?? ""); setSubmittedQuery(data.corrected_query ?? ""); }} className="mt-2 flex items-center gap-1 text-sm font-semibold text-emerald-700 hover:underline" data-testid="fuzzy-suggestion-chip"><Sparkles className="h-3.5 w-3.5" /> Meintest du „{data.corrected_query}“?</button> : <p className="mt-2 text-sm text-slate-500">Preise und Entfernungen von Märkten in deiner Nähe im Vergleich</p>}</div><div className="flex flex-wrap items-center gap-2"><div className="flex rounded-xl border border-slate-200 bg-white p-1"><button type="button" onClick={() => setViewMode("cards")} className={`rounded-lg p-2 transition ${viewMode === "cards" ? "bg-emerald-100 text-emerald-700" : "text-slate-400 hover:text-slate-700"}`} aria-label="Große Kartenansicht" data-testid="view-toggle-cards"><LayoutGrid className="h-4 w-4" /></button><button type="button" onClick={() => setViewMode("table")} className={`rounded-lg p-2 transition ${viewMode === "table" ? "bg-emerald-100 text-emerald-700" : "text-slate-400 hover:text-slate-700"}`} aria-label="Kompakte Tabellenansicht" data-testid="view-toggle-table"><List className="h-4 w-4" /></button></div><div className="relative flex items-center rounded-xl border border-slate-200 bg-white px-3"><ArrowDownUp className="mr-2 h-3.5 w-3.5 text-emerald-600" /><select value={sortBy} onChange={(event) => setSortBy(event.target.value as SortOption)} className="h-10 bg-transparent pr-1 text-sm font-semibold text-slate-600 outline-none" aria-label="Sortierung" data-testid="sort-by-select"><option value="price">Günstigster Gesamtpreis</option><option value="unit">Bester Stückpreis</option><option value="distance">Nächste Filiale</option><option value="discount">Höchster Rabatt</option></select></div></div></div>

          {isLoading ? <div className="grid gap-5 md:grid-cols-2 xl:grid-cols-3"><div className="h-[520px] animate-pulse rounded-[1.35rem] bg-slate-200/70" /><div className="hidden h-[520px] animate-pulse rounded-[1.35rem] bg-slate-200/70 md:block" /><div className="hidden h-[520px] animate-pulse rounded-[1.35rem] bg-slate-200/70 xl:block" /></div> : isError ? <div className="rounded-3xl border border-amber-200 bg-amber-50 p-8 text-center"><Tag className="mx-auto h-8 w-8 text-amber-600" /><h3 className="mt-3 text-lg font-bold text-amber-900">Angebote gerade nicht erreichbar</h3><p className="mt-1 text-sm text-amber-800">Die Oberfläche bleibt verfügbar. Bitte versuche die Suche gleich noch einmal.</p></div> : products.length === 0 ? <div className="rounded-3xl border border-dashed border-slate-300 bg-white p-12 text-center"><Search className="mx-auto h-8 w-8 text-slate-400" /><h3 className="mt-3 text-lg font-bold text-slate-800">Keine passenden Produkte gefunden</h3><p className="mt-1 text-sm text-slate-500">Probiere zum Beispiel „Pizza“, „Milch“, „Hafermilch“, „Shampoo“ oder „Waschmittel“.</p></div> : viewMode === "cards" ? <><>{data?.available_stores.length === 0 ? <div className="mb-5 rounded-2xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-800" data-testid="catalog-without-regional-stores">Der weltweite Produktkatalog ist verfügbar; für {location?.city.name} fehlen noch regionale Demo-Filialen.</div> : null}</><div className="grid gap-5 md:grid-cols-2 xl:grid-cols-3">{products.map((product) => <ProductCard key={product.id} product={product} isFavorite={favoriteIds.has(product.id)} onToggleFavorite={() => toggleFavorite(product.id)} />)}</div></> : <ComparisonTable products={products} favoriteIds={favoriteIds} onToggleFavorite={toggleFavorite} />}
          {data && products.length > 0 ? <div className="mt-8 flex items-center justify-center gap-3" data-testid="catalog-pagination"><Button variant="outline" disabled={page <= 1 || isLoading} onClick={() => { setPage((current) => Math.max(1, current - 1)); window.scrollTo({ top: 650, behavior: "smooth" }); }} data-testid="catalog-previous-page">Zurück</Button><span className="rounded-full bg-white px-4 py-2 text-sm font-bold text-slate-600 shadow-sm" data-testid="catalog-page-number">Seite {page}</span><Button disabled={!data.has_more || isLoading} onClick={() => { setPage((current) => current + 1); window.scrollTo({ top: 650, behavior: "smooth" }); }} className="bg-emerald-600 hover:bg-emerald-700" data-testid="catalog-next-page">Weitere Produkte</Button></div> : null}
        </section>

        <div className="mt-10 flex flex-col gap-3 rounded-2xl border border-emerald-100 bg-emerald-50/70 px-5 py-4 text-sm text-emerald-800 sm:flex-row sm:items-center" data-testid="demo-data-notice"><div className="flex items-center gap-2 font-bold"><Sparkles className="h-4 w-4" /> Produktkatalog & Demo-Filialen</div><p className="text-emerald-800/80">{location ? `${location.city.name}, ${location.country.local_name}` : "Region auswählen"} · {data?.catalog_source ?? "Open Food Facts"} · Preise, Adressen und Bestände sind Demo-Daten</p></div>
        <div className="mt-4 flex items-start gap-2 rounded-2xl bg-white px-5 py-4 text-xs leading-relaxed text-slate-500" data-testid="open-food-facts-attribution"><Store className="mt-0.5 h-4 w-4 shrink-0 text-emerald-600" /><p>Produktinformationen und Bilder: <a href="https://world.openfoodfacts.org" target="_blank" rel="noreferrer" className="font-bold text-emerald-700 hover:underline">Open Food Facts</a>, Open Products Facts und Open Beauty Facts (ODbL/DBCL; Bilder CC BY-SA). Filialpreise, Adressen und Verfügbarkeiten sind simulierte Demo-Daten und keine Live-Bestandszusage.</p></div>
      </main>
      {watchlistOpen ? <Watchlist products={data?.results ?? []} favoriteIds={favoriteIds} onClose={() => setWatchlistOpen(false)} onToggleFavorite={toggleFavorite} /> : null}
      {locationOpen ? <LocationGate languageCode={languageCode} onLanguageChange={setLanguageCode} onComplete={(nextLocation) => { setLocation(nextLocation); setLocationOpen(false); setFavoriteIds(new Set()); setPage(1); }} /> : null}
    </div>
  );
}