export type LanguageCode = "de" | "en" | "fr" | "it" | "es" | "tr" | "nl" | "pl" | "pt";

export interface AppLanguage {
  code: LanguageCode;
  native_name: string;
  english_name: string;
  symbol: string;
}

export const LANGUAGES: AppLanguage[] = [
  { code: "de", native_name: "Deutsch", english_name: "German", symbol: "DE" },
  { code: "en", native_name: "English", english_name: "English", symbol: "EN" },
  { code: "fr", native_name: "Français", english_name: "French", symbol: "FR" },
  { code: "it", native_name: "Italiano", english_name: "Italian", symbol: "IT" },
  { code: "es", native_name: "Español", english_name: "Spanish", symbol: "ES" },
  { code: "tr", native_name: "Türkçe", english_name: "Turkish", symbol: "TR" },
  { code: "nl", native_name: "Nederlands", english_name: "Dutch", symbol: "NL" },
  { code: "pl", native_name: "Polski", english_name: "Polish", symbol: "PL" },
  { code: "pt", native_name: "Português", english_name: "Portuguese", symbol: "PT" },
];

interface LocationCopy {
  languageStep: string;
  languageTitle: string;
  languageSubtitle: string;
  searchLanguage: string;
  countryStep: string;
  countryTitle: string;
  countrySubtitle: string;
  searchCountry: string;
  changeLanguage: string;
  cityStep: string;
  cityTitle: string;
  citiesIn: string;
  searchCity: string;
  changeCountry: string;
  loading: string;
  unavailable: string;
  noResult: string;
  source: string;
}

const ENGLISH_COPY: LocationCopy = {
  languageStep: "Step 1 of 3", languageTitle: "Choose your language", languageSubtitle: "You can change it again later in the header.", searchLanguage: "Search language …",
  countryStep: "Step 2 of 3", countryTitle: "Which country do you live in?", countrySubtitle: "We will only show supermarkets available in your region.", searchCountry: "Search country by name …", changeLanguage: "Change language",
  cityStep: "Step 3 of 3", cityTitle: "Choose your city", citiesIn: "Cities in", searchCity: "Search city …", changeCountry: "Change country",
  loading: "Loading …", unavailable: "Data is currently unavailable. Please try again shortly.", noResult: "No matching result found.", source: "Country and city data: countries.dev",
};

export const LOCATION_COPY: Record<LanguageCode, LocationCopy> = {
  de: { languageStep: "Schritt 1 von 3", languageTitle: "Wähle deine Sprache", languageSubtitle: "Du kannst sie später jederzeit im Kopfbereich ändern.", searchLanguage: "Sprache suchen …", countryStep: "Schritt 2 von 3", countryTitle: "In welchem Land lebst du?", countrySubtitle: "Damit zeigen wir dir nur Supermärkte, die in deiner Region verfügbar sind.", searchCountry: "Land nach Namen suchen …", changeLanguage: "Sprache ändern", cityStep: "Schritt 3 von 3", cityTitle: "Wähle deine Stadt", citiesIn: "Städte in", searchCity: "Stadt suchen …", changeCountry: "Land ändern", loading: "Wird geladen …", unavailable: "Daten sind gerade nicht erreichbar. Bitte versuche es gleich noch einmal.", noResult: "Kein passender Eintrag gefunden.", source: "Länder- und Städtedaten: countries.dev" },
  en: ENGLISH_COPY,
  fr: { ...ENGLISH_COPY, languageStep: "Étape 1 sur 3", languageTitle: "Choisissez votre langue", languageSubtitle: "Vous pourrez la modifier plus tard dans l’en-tête.", searchLanguage: "Rechercher une langue …", countryStep: "Étape 2 sur 3", countryTitle: "Dans quel pays vivez-vous ?", countrySubtitle: "Nous affichons uniquement les supermarchés disponibles dans votre région.", searchCountry: "Rechercher un pays …", changeLanguage: "Changer de langue", cityStep: "Étape 3 sur 3", cityTitle: "Choisissez votre ville", citiesIn: "Villes en", searchCity: "Rechercher une ville …", changeCountry: "Changer de pays", loading: "Chargement …", unavailable: "Données momentanément indisponibles.", noResult: "Aucun résultat correspondant.", source: "Données pays et villes : countries.dev" },
  it: { ...ENGLISH_COPY, languageStep: "Passaggio 1 di 3", languageTitle: "Scegli la tua lingua", languageSubtitle: "Potrai cambiarla in seguito nell’intestazione.", searchLanguage: "Cerca lingua …", countryStep: "Passaggio 2 di 3", countryTitle: "In quale paese vivi?", countrySubtitle: "Mostriamo solo i supermercati disponibili nella tua zona.", searchCountry: "Cerca paese …", changeLanguage: "Cambia lingua", cityStep: "Passaggio 3 di 3", cityTitle: "Scegli la tua città", citiesIn: "Città in", searchCity: "Cerca città …", changeCountry: "Cambia paese", loading: "Caricamento …", unavailable: "Dati temporaneamente non disponibili.", noResult: "Nessun risultato corrispondente.", source: "Dati paesi e città: countries.dev" },
  es: { ...ENGLISH_COPY, languageStep: "Paso 1 de 3", languageTitle: "Elige tu idioma", languageSubtitle: "Puedes cambiarlo más tarde en la cabecera.", searchLanguage: "Buscar idioma …", countryStep: "Paso 2 de 3", countryTitle: "¿En qué país vives?", countrySubtitle: "Solo mostramos supermercados disponibles en tu región.", searchCountry: "Buscar país …", changeLanguage: "Cambiar idioma", cityStep: "Paso 3 de 3", cityTitle: "Elige tu ciudad", citiesIn: "Ciudades en", searchCity: "Buscar ciudad …", changeCountry: "Cambiar país", loading: "Cargando …", unavailable: "Datos no disponibles temporalmente.", noResult: "No se encontró ningún resultado.", source: "Datos de países y ciudades: countries.dev" },
  tr: { ...ENGLISH_COPY, languageStep: "3 adımın 1.si", languageTitle: "Dilini seç", languageSubtitle: "Daha sonra üst menüden değiştirebilirsin.", searchLanguage: "Dil ara …", countryStep: "3 adımın 2.si", countryTitle: "Hangi ülkede yaşıyorsun?", countrySubtitle: "Yalnızca bölgende bulunan marketleri gösteririz.", searchCountry: "Ülke ara …", changeLanguage: "Dili değiştir", cityStep: "3 adımın 3.sü", cityTitle: "Şehrini seç", citiesIn: "Şehirler:", searchCity: "Şehir ara …", changeCountry: "Ülkeyi değiştir", loading: "Yükleniyor …", unavailable: "Veriler şu anda kullanılamıyor.", noResult: "Eşleşen sonuç bulunamadı.", source: "Ülke ve şehir verileri: countries.dev" },
  nl: { ...ENGLISH_COPY, languageStep: "Stap 1 van 3", languageTitle: "Kies je taal", languageSubtitle: "Je kunt deze later in de kop wijzigen.", searchLanguage: "Taal zoeken …", countryStep: "Stap 2 van 3", countryTitle: "In welk land woon je?", countrySubtitle: "We tonen alleen supermarkten die in jouw regio beschikbaar zijn.", searchCountry: "Land zoeken …", changeLanguage: "Taal wijzigen", cityStep: "Stap 3 van 3", cityTitle: "Kies je stad", citiesIn: "Steden in", searchCity: "Stad zoeken …", changeCountry: "Land wijzigen", loading: "Laden …", unavailable: "Gegevens zijn tijdelijk niet beschikbaar.", noResult: "Geen passend resultaat gevonden.", source: "Land- en stadsgegevens: countries.dev" },
  pl: { ...ENGLISH_COPY, languageStep: "Krok 1 z 3", languageTitle: "Wybierz język", languageSubtitle: "Możesz go później zmienić w nagłówku.", searchLanguage: "Szukaj języka …", countryStep: "Krok 2 z 3", countryTitle: "W jakim kraju mieszkasz?", countrySubtitle: "Pokażemy tylko sklepy dostępne w Twoim regionie.", searchCountry: "Szukaj kraju …", changeLanguage: "Zmień język", cityStep: "Krok 3 z 3", cityTitle: "Wybierz miasto", citiesIn: "Miasta w", searchCity: "Szukaj miasta …", changeCountry: "Zmień kraj", loading: "Ładowanie …", unavailable: "Dane są chwilowo niedostępne.", noResult: "Nie znaleziono pasującego wyniku.", source: "Dane krajów i miast: countries.dev" },
  pt: { ...ENGLISH_COPY, languageStep: "Passo 1 de 3", languageTitle: "Escolha o seu idioma", languageSubtitle: "Pode alterá-lo mais tarde no cabeçalho.", searchLanguage: "Pesquisar idioma …", countryStep: "Passo 2 de 3", countryTitle: "Em que país vive?", countrySubtitle: "Mostramos apenas supermercados disponíveis na sua região.", searchCountry: "Pesquisar país …", changeLanguage: "Alterar idioma", cityStep: "Passo 3 de 3", cityTitle: "Escolha a sua cidade", citiesIn: "Cidades em", searchCity: "Pesquisar cidade …", changeCountry: "Alterar país", loading: "A carregar …", unavailable: "Dados temporariamente indisponíveis.", noResult: "Nenhum resultado encontrado.", source: "Dados de países e cidades: countries.dev" },
};