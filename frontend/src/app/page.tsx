"use client";

import { useCallback, useEffect, useMemo, useState } from "react";

import { CategoryBreakdownChart } from "@/components/CategoryBreakdownChart";
import { CategoryReviewPanel } from "@/components/CategoryReviewPanel";
import { DashboardPeriodFilter } from "@/components/DashboardPeriodFilter";
import { ExpenseChart } from "@/components/ExpenseChart";
import { TransactionTable } from "@/components/TransactionTable";
import { api } from "@/lib/api";
import { dateRangeFromYearMonth } from "@/lib/dashboard-period";
import {
  Account,
  Category,
  CategoryBreakdown,
  MonthlySummary,
  RecategorizationSuggestion,
  Transaction,
} from "@/types";
import { Card, CardContent } from "@/components/ui/card";
import { Alert, AlertDescription } from "@/components/ui/alert";
export default function HomePage() {
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [summary, setSummary] = useState<MonthlySummary[]>([]);
  const [categoryBreakdown, setCategoryBreakdown] = useState<CategoryBreakdown[]>([]);
  const [reviewSuggestions, setReviewSuggestions] = useState<RecategorizationSuggestion[]>([]);
  const [error, setError] = useState<string>("");
  const [loading, setLoading] = useState(true);
  const [yearFilter, setYearFilter] = useState("");
  const [monthFilter, setMonthFilter] = useState("");

  const dateRange = useMemo(() => dateRangeFromYearMonth(yearFilter, monthFilter), [yearFilter, monthFilter]);

  const totals = useMemo(() => {
    const income = transactions.filter((t) => Number(t.amount) > 0).reduce((acc, t) => acc + Number(t.amount), 0);
    const expense = transactions.filter((t) => Number(t.amount) < 0).reduce((acc, t) => acc + Math.abs(Number(t.amount)), 0);
    return { income, expense, net: income - expense };
  }, [transactions]);

  const loadData = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const [tx, cats, accs, monthly, breakdown, suggestions] = await Promise.all([
        api.listTransactions({ limit: 1000, dateRange }),
        api.listCategories(),
        api.listAccounts(),
        api.listMonthlySummary(dateRange),
        api.listCategoryBreakdown(dateRange),
        api.listRecategorizationSuggestions(dateRange),
      ]);
      setTransactions(tx);
      setCategories(cats);
      setAccounts(accs);
      setSummary(monthly);
      setCategoryBreakdown(breakdown.map((item) => ({ ...item, total: Math.abs(Number(item.total)) })));
      setReviewSuggestions(suggestions);
    } catch (err) {
      const message = err instanceof Error ? err.message : "Failed to load data";
      setError(message);
    } finally {
      setLoading(false);
    }
  }, [dateRange]);

  useEffect(() => {
    void loadData();
  }, [loadData]);

  return (
    <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
      <section className="mb-8 rounded-3xl border border-primary/20 bg-gradient-to-br from-primary/15 via-card to-card px-6 py-8 shadow-xl">
        <h1 className="text-3xl font-bold text-foreground">Dashboard</h1>
        <p className="mt-2 text-muted-foreground">
          Track expenses and income, review categories, and explore trends. Use Import or Export in the top menu for
          data transfer.
        </p>
      </section>

      <section className="mb-8">
        <DashboardPeriodFilter
          year={yearFilter}
          month={monthFilter}
          onYearChange={setYearFilter}
          onMonthChange={setMonthFilter}
        />
      </section>

      {error ? (
        <Alert className="mb-4">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      ) : null}

      <section className="mb-8 grid gap-4 sm:grid-cols-3">
        <MetricCard title="Income" value={totals.income} accent="text-emerald-400" glow="shadow-emerald-500/10" />
        <MetricCard title="Expenses" value={totals.expense} accent="text-red-400" glow="shadow-red-500/10" />
        <MetricCard title="Net" value={totals.net} accent={totals.net >= 0 ? "text-emerald-400" : "text-red-400"} glow={totals.net >= 0 ? "shadow-emerald-500/10" : "shadow-red-500/10"} />
      </section>

      <section className="mb-8 grid gap-6 lg:grid-cols-2">
        <ExpenseChart data={summary} />
        <CategoryBreakdownChart data={categoryBreakdown} />
      </section>

      <section className="mb-8">
        <CategoryReviewPanel
          suggestions={reviewSuggestions}
          categories={categories}
          onApplied={loadData}
          dateRange={dateRange}
          onSuggestionsChange={setReviewSuggestions}
        />
      </section>

      <section>
        {loading ? (
          <Card>
            <CardContent className="p-4">
              <p className="text-sm text-muted-foreground">Loading transactions...</p>
            </CardContent>
          </Card>
        ) : (
          <TransactionTable transactions={transactions} categories={categories} accounts={accounts} onUpdated={loadData} />
        )}
      </section>
    </main>
  );
}

function MetricCard({ title, value, accent, glow }: { title: string; value: number; accent: string; glow: string }) {
  return (
    <Card className={`border-border/60 bg-card/80 backdrop-blur-sm shadow-lg ${glow}`}>
      <CardContent className="pt-5 pb-5">
        <p className="text-sm font-medium text-muted-foreground">{title}</p>
        <p className={`mt-1 text-2xl font-semibold ${accent}`}>
          {value.toLocaleString("en-CA", { style: "currency", currency: "CAD" })}
        </p>
      </CardContent>
    </Card>
  );
}
