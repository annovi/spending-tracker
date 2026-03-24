import {
  Account,
  BulkRecategorizeItem,
  Category,
  CategoryBreakdown,
  MonthlySummary,
  RecategorizationSuggestion,
  Transaction,
} from "@/types";
import { appendDateRange, type DateRangeParams } from "@/lib/dashboard-period";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export type CsvColumnMapping = {
  date?: string;
  description?: string;
  amount?: string;
  debit?: string;
  credit?: string;
};

export type CsvPreviewResponse = {
  columns: string[];
  sample_rows: Record<string, string>[];
  detected_mapping?: CsvColumnMapping;
};

export type ImportBatchResult = {
  rows_imported: number;
  duplicates_skipped: number;
};

export function formatImportResult(result: ImportBatchResult): string {
  return `Imported ${result.rows_imported} rows, skipped ${result.duplicates_skipped} duplicates.`;
}

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

async function multipartRequestJson<T>(path: string, form: FormData): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: "POST",
    body: form,
    cache: "no-store",
  });

  if (!response.ok) {
    const message = await response.text();
    throw new Error(message || "Request failed");
  }

  return response.json() as Promise<T>;
}

function withDateRange(path: string, range: DateRangeParams): string {
  const params = new URLSearchParams();
  appendDateRange(params, range);
  const qs = params.toString();
  return qs ? `${path}?${qs}` : path;
}

export const api = {
  listTransactions: (opts?: { limit?: number; dateRange?: DateRangeParams }) => {
    const params = new URLSearchParams();
    if (opts?.limit != null) {
      params.set("limit", String(opts.limit));
    }
    appendDateRange(params, opts?.dateRange ?? {});
    const qs = params.toString();
    return request<Transaction[]>(`/transactions${qs ? `?${qs}` : ""}`);
  },
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
  listMonthlySummary: (dateRange?: DateRangeParams) =>
    request<MonthlySummary[]>(withDateRange("/analytics/summary", dateRange ?? {})),
  listCategoryBreakdown: (dateRange?: DateRangeParams) =>
    request<CategoryBreakdown[]>(withDateRange("/analytics/categories", dateRange ?? {})),
  listRecategorizationSuggestions: (dateRange?: DateRangeParams, recompute?: boolean) => {
    const params = new URLSearchParams();
    appendDateRange(params, dateRange ?? {});
    if (recompute) {
      params.set("recompute", "true");
    }
    const qs = params.toString();
    return request<RecategorizationSuggestion[]>(
      `/transactions/review/suggestions${qs ? `?${qs}` : ""}`
    );
  },
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
    return multipartRequestJson<ImportBatchResult>("/imports/csv", form);
  },
  previewCsv: async (file: File) => {
    const form = new FormData();
    form.append("file", file);
    return multipartRequestJson<CsvPreviewResponse>("/imports/csv/preview", form);
  },
  uploadCsvWithMapping: async (file: File, mapping: Record<string, string>, accountId?: number) => {
    const form = new FormData();
    form.append("file", file);
    form.append("mapping", JSON.stringify(mapping));
    if (accountId) {
      form.append("account_id", String(accountId));
    }
    return multipartRequestJson<ImportBatchResult>("/imports/csv/with-mapping", form);
  },
  listBankPresets: () => request<{ presets: { id: string; label: string }[] }>("/imports/bank-presets"),
  uploadCsvWithBankPreset: async (file: File, bankPreset: string, accountId?: number) => {
    const form = new FormData();
    form.append("file", file);
    form.append("bank_preset", bankPreset);
    if (accountId) {
      form.append("account_id", String(accountId));
    }
    return multipartRequestJson<ImportBatchResult>("/imports/csv/bank", form);
  },
  googleSheetsStatus: () =>
    request<{ configured: boolean; has_default_folder: boolean }>("/google-sheets/status"),
  listGoogleSpreadsheets: (folderId?: string) => {
    const params = new URLSearchParams();
    if (folderId !== undefined && folderId.trim() !== "") {
      params.set("folder_id", folderId.trim());
    }
    const qs = params.toString();
    return request<{ spreadsheets: { id: string; name: string }[] }>(
      `/google-sheets/spreadsheets${qs ? `?${qs}` : ""}`
    );
  },
  listGoogleWorksheets: (spreadsheetId: string) =>
    request<{ worksheets: { title: string; row_count: number }[] }>(
      `/google-sheets/worksheets?spreadsheet_id=${encodeURIComponent(spreadsheetId)}`
    ),
  importGoogleSheet: (body: {
    spreadsheet_id: string;
    worksheet_name?: string;
    account_id?: number;
  }) =>
    request<ImportBatchResult>("/google-sheets/import", {
      method: "POST",
      body: JSON.stringify(body),
    }),
  exportGoogleSheet: (body: {
    spreadsheet_id: string;
    worksheet_name: string;
    date_from?: string;
    date_to?: string;
  }) =>
    request<{ rows_written: number }>("/google-sheets/export", {
      method: "POST",
      body: JSON.stringify(body),
    }),
};
