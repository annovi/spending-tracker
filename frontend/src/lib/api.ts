import {
  Account,
  BulkRecategorizeItem,
  Category,
  CategoryBreakdown,
  MonthlySummary,
  RecategorizationSuggestion,
  Transaction,
} from "@/types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {}),
    },
    cache: "no-store",
  });

  if (!response.ok) {
    const message = await response.text();
    throw new Error(message || "Request failed");
  }

  return response.json() as Promise<T>;
}

export const api = {
  listTransactions: () => request<Transaction[]>("/transactions"),
  updateTransaction: (id: number, payload: Partial<Transaction>) =>
    request<Transaction>(`/transactions/${id}`, {
      method: "PATCH",
      body: JSON.stringify(payload),
    }),
  listCategories: () => request<Category[]>("/categories"),
  createCategory: (payload: { name: string; type: "expense" | "income"; color?: string; icon?: string }) =>
    request<Category>("/categories", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  updateCategory: (id: number, payload: { name?: string; type?: "expense" | "income"; color?: string; icon?: string }) =>
    request<Category>(`/categories/${id}`, {
      method: "PATCH",
      body: JSON.stringify(payload),
    }),
  deleteCategory: (id: number) =>
    request<{ ok: boolean }>(`/categories/${id}`, {
      method: "DELETE",
    }),
  listAccounts: () => request<Account[]>("/accounts"),
  createAccount: (payload: { name: string; type: "bank" | "credit_card" | "cash" }) =>
    request<Account>("/accounts", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  updateAccount: (id: number, payload: { name?: string; type?: "bank" | "credit_card" | "cash" }) =>
    request<Account>(`/accounts/${id}`, {
      method: "PATCH",
      body: JSON.stringify(payload),
    }),
  deleteAccount: (id: number) =>
    request<{ ok: boolean }>(`/accounts/${id}`, {
      method: "DELETE",
    }),
  listMonthlySummary: () => request<MonthlySummary[]>("/analytics/summary"),
  listCategoryBreakdown: () => request<CategoryBreakdown[]>("/analytics/categories"),
  listRecategorizationSuggestions: () => request<RecategorizationSuggestion[]>("/transactions/review/suggestions"),
  applyRecategorizationSuggestions: (items: BulkRecategorizeItem[]) =>
    request<{ updated: number }>("/transactions/review/apply", {
      method: "POST",
      body: JSON.stringify({ items }),
    }),
  uploadCsv: async (file: File, accountId?: number) => {
    const form = new FormData();
    form.append("file", file);
    if (accountId) {
      form.append("account_id", String(accountId));
    }

    const response = await fetch(`${API_BASE_URL}/imports/csv`, {
      method: "POST",
      body: form,
      cache: "no-store",
    });

    if (!response.ok) {
      const message = await response.text();
      throw new Error(message || "Upload failed");
    }

    return response.json() as Promise<{ rows_imported: number; duplicates_skipped: number }>;
  },
  previewCsv: async (file: File) => {
    const form = new FormData();
    form.append("file", file);

    const response = await fetch(`${API_BASE_URL}/imports/csv/preview`, {
      method: "POST",
      body: form,
      cache: "no-store",
    });

    if (!response.ok) {
      const message = await response.text();
      throw new Error(message || "Preview failed");
    }

    return response.json() as Promise<{
      columns: string[];
      sample_rows: Record<string, string>[];
      detected_mapping?: {
        date?: string;
        description?: string;
        amount?: string;
        debit?: string;
        credit?: string;
      };
    }>;
  },
  uploadCsvWithMapping: async (file: File, mapping: Record<string, string>, accountId?: number) => {
    const form = new FormData();
    form.append("file", file);
    form.append("mapping", JSON.stringify(mapping));
    if (accountId) {
      form.append("account_id", String(accountId));
    }

    const response = await fetch(`${API_BASE_URL}/imports/csv/with-mapping`, {
      method: "POST",
      body: form,
      cache: "no-store",
    });

    if (!response.ok) {
      const message = await response.text();
      throw new Error(message || "Upload failed");
    }

    return response.json() as Promise<{ rows_imported: number; duplicates_skipped: number }>;
  },
};
