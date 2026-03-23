"use client";

import { ChangeEvent, useEffect, useMemo, useState } from "react";

import { api } from "@/lib/api";
import { BulkRecategorizeItem, Category, RecategorizationSuggestion } from "@/types";

interface CategoryReviewPanelProps {
  suggestions: RecategorizationSuggestion[];
  categories: Category[];
  onApplied: () => Promise<void>;
}

export function CategoryReviewPanel({ suggestions, categories, onApplied }: CategoryReviewPanelProps) {
  const [localSuggestions, setLocalSuggestions] = useState<RecategorizationSuggestion[]>(suggestions);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");

  useEffect(() => {
    setLocalSuggestions(suggestions);
  }, [suggestions]);

  const categoryOptions = useMemo(() => {
    return categories.map((category) => ({ id: category.id, name: category.name }));
  }, [categories]);

  const pendingItems = useMemo<BulkRecategorizeItem[]>(() => {
    return localSuggestions.map((item) => ({
      transaction_id: item.transaction_id,
      category_id: item.suggested_category_id,
    }));
  }, [localSuggestions]);

  async function applyAll() {
    if (!pendingItems.length) {
      return;
    }

    setLoading(true);
    setMessage("");
    try {
      const result = await api.applyRecategorizationSuggestions(pendingItems);
      setMessage(`Updated ${result.updated} transactions.`);
      await onApplied();
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Failed to apply updates");
    } finally {
      setLoading(false);
    }
  }

  function changeSuggestedCategory(transactionId: number, nextCategoryId: number) {
    setLocalSuggestions((current) =>
      current.map((item) =>
        item.transaction_id === transactionId
          ? {
            ...item,
            suggested_category_id: nextCategoryId,
            suggested_category_name: categoryOptions.find((option) => option.id === nextCategoryId)?.name ?? item.suggested_category_name,
          }
          : item,
      ),
    );
  }

  if (!localSuggestions.length) {
    return (
      <div className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
        <h2 className="text-lg font-semibold text-slate-900">Category Review</h2>
        <p className="mt-2 text-sm text-slate-600">No recategorization suggestions right now.</p>
      </div>
    );
  }

  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
      <div className="flex items-center justify-between gap-3">
        <div>
          <h2 className="text-lg font-semibold text-slate-900">Category Review</h2>
          <p className="mt-1 text-sm text-slate-600">Review AI suggestions and apply corrections in bulk.</p>
        </div>
        <button
          type="button"
          onClick={applyAll}
          disabled={loading || !pendingItems.length}
          className="rounded-lg bg-slate-900 px-4 py-2 text-sm font-medium text-white disabled:opacity-50"
        >
          {loading ? "Applying..." : `Apply ${pendingItems.length} Suggestions`}
        </button>
      </div>

      <div className="mt-4 overflow-x-auto">
        <table className="min-w-full divide-y divide-slate-200 text-sm">
          <thead>
            <tr className="text-left text-slate-500">
              <th className="py-2 pr-4">Date</th>
              <th className="py-2 pr-4">Description</th>
              <th className="py-2 pr-4">Current</th>
              <th className="py-2 pr-4">Suggested</th>
              <th className="py-2 pr-4">Amount</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {localSuggestions.map((item) => (
              <tr key={item.transaction_id}>
                <td className="py-2 pr-4 text-slate-600">{item.date}</td>
                <td className="py-2 pr-4 text-slate-700">{item.description}</td>
                <td className="py-2 pr-4 text-slate-500">{item.current_category_name ?? "Uncategorized"}</td>
                <td className="py-2 pr-4">
                  <select
                    value={item.suggested_category_id}
                    onChange={(event: ChangeEvent<HTMLSelectElement>) =>
                      changeSuggestedCategory(item.transaction_id, Number(event.target.value))
                    }
                    className="rounded-md border border-slate-300 px-2 py-1"
                  >
                    {categoryOptions.map((option) => (
                      <option key={option.id} value={option.id}>
                        {option.name}
                      </option>
                    ))}
                  </select>
                </td>
                <td className={`py-2 pr-4 font-medium ${item.amount < 0 ? "text-red-600" : "text-emerald-600"}`}>
                  {Number(item.amount).toLocaleString(undefined, { style: "currency", currency: "USD" })}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {message ? <p className="mt-3 text-sm text-slate-700">{message}</p> : null}
    </div>
  );
}
