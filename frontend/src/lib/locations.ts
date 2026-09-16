import { apiGet } from "@/lib/api";

export interface Country {
  code: string;
  local_name: string;
  english_name: string;
  flag_url: string;
}

export interface City {
  id: string;
  name: string;
  population: number;
}

export interface RegionMarkets {
  country_code: string;
  city: string;
  stores: string[];
  data_source: string;
}

export interface SelectedLocation {
  country: Country;
  city: City;
}

export const fetchCountries = () => apiGet<Country[]>("/locations/countries");
export const fetchCities = (countryCode: string) =>
  apiGet<City[]>(`/locations/cities?country=${encodeURIComponent(countryCode)}`);
export const fetchRegionMarkets = (countryCode: string, city: string) =>
  apiGet<RegionMarkets>(
    `/locations/markets?country=${encodeURIComponent(countryCode)}&city=${encodeURIComponent(city)}`,
  );