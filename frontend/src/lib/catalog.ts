import { apiGet } from "@/lib/api";

export interface CatalogSubcategory {
  slug: string;
  name: string;
  search_term: string;
}

export interface CatalogCategory {
  slug: string;
  name: string;
  description: string;
  icon: string;
  subcategories: CatalogSubcategory[];
}

export const fetchCatalogCategories = () => apiGet<CatalogCategory[]>("/catalog/categories");