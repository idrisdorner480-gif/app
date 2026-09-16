import { apiGet } from "@/lib/api";

export interface StoreOffer {
  store: string;
  country_code: string;
  branch_id: string;
  branch_name: string;
  address: string;
  price: number;
  unit_price: number;
  distance_km: number;
  available: boolean;
  stock_status: "verfügbar" | "knapp" | "nicht verfügbar";
  discount_percent: number;
}

export interface Product {
  id: string;
  name: string;
  brand: string;
  category: string;
  package_size: string;
  image_url: string;
  barcode: string | null;
  data_source: string;
  product_url: string | null;
  keywords: string[];
  offers: StoreOffer[];
}

export interface ProductSearchResponse {
  query: string;
  corrected_query: string | null;
  results: Product[];
  total: number;
  data_source: string;
  country_code: string;
  city: string;
  available_stores: string[];
  page: number;
  page_size: number;
  has_more: boolean;
  catalog_source: string;
}

export const fetchProducts = (query: string, countryCode: string, city: string, page: number, pageSize = 24, category?: string) =>
  apiGet<ProductSearchResponse>(
    `/products/search?q=${encodeURIComponent(query)}&country=${encodeURIComponent(countryCode)}&city=${encodeURIComponent(city)}&page=${page}&page_size=${pageSize}${category ? `&category=${encodeURIComponent(category)}` : ""}`,
  );