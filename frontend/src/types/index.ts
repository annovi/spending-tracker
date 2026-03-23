export type CategoryType = "expense" | "income";

export interface Category {
  id: number;
  name: string;
  type: CategoryType;
  color: string;
  icon?: string | null;
}

export interface Account {
  id: number;
  name: string;
  type: "bank" | "credit_card" | "cash";
}

export interface Transaction {
  id: number;
  date: string;
  description: string;
  display_name?: string | null;
  amount: number;
  category_id?: number | null;
  account_id?: number | null;
  notes?: string | null;
  is_reviewed: boolean;
  source: string;
  import_hash?: string | null;
  created_at: string;
  updated_at: string;
}

export interface MonthlySummary {
  month: string;
  income: number;
  expense: number;
  net: number;
}

export interface CategoryBreakdown {
  category: string;
  total: number;
}

export interface RecategorizationSuggestion {
  transaction_id: number;
  date: string;
  description: string;
  amount: number;
  current_category_id?: number | null;
  current_category_name?: string | null;
  suggested_category_id: number;
  suggested_category_name: string;
}

export interface BulkRecategorizeItem {
  transaction_id: number;
  category_id: number;
}
