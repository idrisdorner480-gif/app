import { apiGet } from "@/lib/api";

export interface StoreOffer {
  store: string;
  price: number;
  unit_price: number;
  distance_km: number;
  available: boolean;
  discount_percent: number;
}

export interface Product {
  id: string;
  name: string;
  brand: string;
  category: string;
  package_size: string;
  image_url: string;
  keywords: string[];
  offers: StoreOffer[];
}

export interface ProductSearchResponse {
  query: string;
  corrected_query: string | null;
  results: Product[];
  total: number;
  data_source: string;
}

export const fetchProducts = (query: string) =>
  apiGet<ProductSearchResponse>(`/products/search?q=${encodeURIComponent(query)}`);