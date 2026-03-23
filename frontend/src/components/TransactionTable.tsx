"use client";

import { ChangeEvent, FocusEvent, useMemo } from "react";

import { api } from "@/lib/api";
import { Category, Transaction } from "@/types";

interface TransactionTableProps {
  transactions: Transaction[];
  categories: Category[];
  onUpdated: () => Promise<void>;
}

export function TransactionTable({ transactions, categories, onUpdated }: TransactionTableProps) {
  const categoryMap = useMemo(() => {
    return new Map(categories.map((category) => [category.id, category]));
  }, [categories]);

  async function updateDescription(transaction: Transaction, displayName: string) {
    await api.updateTransaction(transaction.id, { display_name: displayName });
    await onUpdated();
  }

  async function updateCategory(transaction: Transaction, categoryId: number) {
    await api.updateTransaction(transaction.id, { category_id: categoryId, is_reviewed: true });
    await onUpdated();
  }

  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
      <h2 className="text-lg font-semibold text-slate-900">Transactions</h2>
      <div className="mt-4 overflow-x-auto">
        <table className="min-w-full divide-y divide-slate-200 text-sm">
          <thead>
            <tr className="text-left text-slate-500">
              <th className="py-2 pr-4">Date</th>
              <th className="py-2 pr-4">Description</th>
              <th className="py-2 pr-4">Amount</th>
              <th className="py-2 pr-4">Category</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {transactions.map((transaction) => (
              <tr key={transaction.id}>
                <td className="py-2 pr-4 text-slate-600">{transaction.date}</td>
                <td className="py-2 pr-4">
                  <input
                    defaultValue={transaction.display_name ?? transaction.description}
                    onBlur={(event: FocusEvent<HTMLInputElement>) => {
                      const value = event.target.value.trim();
                      if (value && value !== transaction.display_name) {
                        void updateDescription(transaction, value);
                      }
                    }}
                    className="w-72 rounded-md border border-slate-300 px-2 py-1"
                  />
                </td>
                <td className={`py-2 pr-4 font-medium ${Number(transaction.amount) < 0 ? "text-red-600" : "text-emerald-600"}`}>
                  {Number(transaction.amount).toLocaleString(undefined, {
                    style: "currency",
                    currency: "USD",
                  })}
                </td>
                <td className="py-2 pr-4">
                  <select
                    value={transaction.category_id ?? ""}
                    onChange={(event: ChangeEvent<HTMLSelectElement>) => {
                      const nextId = Number(event.target.value);
                      if (nextId) {
                        void updateCategory(transaction, nextId);
                      }
                    }}
                    className="rounded-md border border-slate-300 px-2 py-1"
                  >
                    <option value="">Uncategorized</option>
                    {categories.map((category) => (
                      <option key={category.id} value={category.id}>
                        {category.name}
                      </option>
                    ))}
                  </select>
                  {transaction.category_id ? (
                    <span
                      className="ml-2 inline-block h-2.5 w-2.5 rounded-full"
                      style={{ backgroundColor: categoryMap.get(transaction.category_id)?.color ?? "#94a3b8" }}
                    />
                  ) : null}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
