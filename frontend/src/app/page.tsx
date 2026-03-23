"use client";

import { useCallback, useEffect, useMemo, useState } from "react";

import { CategoryBreakdownChart } from "@/components/CategoryBreakdownChart";
import { CategoryReviewPanel } from "@/components/CategoryReviewPanel";
import { CSVUploadAdvanced } from "@/components/CSVUploadAdvanced";
import { ExpenseChart } from "@/components/ExpenseChart";
import { TransactionTable } from "@/components/TransactionTable";
import { api } from "@/lib/api";
import { Category, CategoryBreakdown, MonthlySummary, RecategorizationSuggestion, Transaction } from "@/types";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import Link from "next/link";

export default function HomePage() {
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [summary, setSummary] = useState<MonthlySummary[]>([]);
  const [categoryBreakdown, setCategoryBreakdown] = useState<CategoryBreakdown[]>([]);
  const [reviewSuggestions, setReviewSuggestions] = useState<RecategorizationSuggestion[]>([]);
  const [error, setError] = useState<string>("");
  const [loading, setLoading] = useState(true);

  const totals = useMemo(() => {
    const income = transactions.filter((t) => Number(t.amount) > 0).reduce((acc, t) => acc + Number(t.amount), 0);
    const expense = transactions.filter((t) => Number(t.amount) < 0).reduce((acc, t) => acc + Math.abs(Number(t.amount)), 0);
    return { income, expense, net: income - expense };
  }, [transactions]);

  const loadData = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const [tx, cats, monthly, breakdown, suggestions] = await Promise.all([
        api.listTransactions(),
        api.listCategories(),
        api.listMonthlySummary(),
        api.listCategoryBreakdown(),
        api.listRecategorizationSuggestions(),
      ]);
      setTransactions(tx);
      setCategories(cats);
      setSummary(monthly);
      setCategoryBreakdown(breakdown.map((item) => ({ ...item, total: Math.abs(Number(item.total)) })));
      setReviewSuggestions(suggestions);
    } catch (err) {
      const message = err instanceof Error ? err.message : "Failed to load data";
      setError(message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadData();
  }, [loadData]);

  return (
    <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
      <section className="mb-6 rounded-3xl bg-slate-900 px-6 py-8 text-white shadow-xl">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">Spending Tracker</h1>
            <p className="mt-2 text-slate-300">Track every expense and income, import statements, and keep your data categorized.</p>
          </div>
          <div className="flex gap-2">
            <Button asChild variant="secondary">
              <Link href="/categories">Manage Categories</Link>
            </Button>
            <Button asChild variant="secondary">
              <Link href="/accounts">Manage Accounts</Link>
            </Button>
          </div>
        </div>
      </section>

      {error ? (
        <Alert className="mb-4">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      ) : null}

      <section className="mb-6 grid gap-4 sm:grid-cols-3">
        <MetricCard title="Income" value={totals.income} color="text-emerald-600" />
        <MetricCard title="Expenses" value={totals.expense} color="text-red-600" />
        <MetricCard title="Net" value={totals.net} color={totals.net >= 0 ? "text-emerald-600" : "text-red-600"} />
      </section>

      <section className="mb-6">
        <CSVUploadAdvanced onImported={loadData} />
      </section>

      <section className="mb-6 grid gap-6 lg:grid-cols-2">
        <ExpenseChart data={summary} />
        <CategoryBreakdownChart data={categoryBreakdown} />
      </section>

      <section className="mb-6">
        <CategoryReviewPanel suggestions={reviewSuggestions} categories={categories} onApplied={loadData} />
      </section>

      <section>
        {loading ? (
          <Card>
            <CardContent className="p-4">
              <p className="text-sm text-slate-600">Loading transactions...</p>
            </CardContent>
          </Card>
        ) : (
          <TransactionTable transactions={transactions} categories={categories} onUpdated={loadData} />
        )}
      </section>
    </main>
  );
}

function MetricCard({ title, value, color }: { title: string; value: number; color: string }) {
  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-sm font-medium text-slate-500">{title}</CardTitle>
      </CardHeader>
      <CardContent>
        <p className={`text-2xl font-semibold ${color}`}>
          {value.toLocaleString(undefined, { style: "currency", currency: "USD" })}
        </p>
      </CardContent>
    </Card>
  );
}
