"use client";

import { ChangeEvent, useEffect, useMemo, useState } from "react";

import { api } from "@/lib/api";
import { BulkRecategorizeItem, Category, RecategorizationSuggestion } from "@/types";
import { Button } from "@/components/ui/button";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

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
        <Button
          onClick={applyAll}
          disabled={loading || !pendingItems.length}
        >
          {loading ? "Applying..." : `Apply ${pendingItems.length} Suggestions`}
        </Button>
      </div>

      <div className="mt-4">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Date</TableHead>
              <TableHead>Description</TableHead>
              <TableHead>Current</TableHead>
              <TableHead>Suggested</TableHead>
              <TableHead>Amount</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {localSuggestions.map((item) => (
              <TableRow key={item.transaction_id}>
                <TableCell className="text-slate-600">{item.date}</TableCell>
                <TableCell className="text-slate-700">{item.description}</TableCell>
                <TableCell className="text-slate-500">{item.current_category_name ?? "Uncategorized"}</TableCell>
                <TableCell>
                  <Select
                    value={item.suggested_category_id.toString()}
                    onValueChange={(value) =>
                      changeSuggestedCategory(item.transaction_id, Number(value))
                    }
                  >
                    <SelectTrigger className="w-[180px]">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {categoryOptions.map((option) => (
                        <SelectItem key={option.id} value={option.id.toString()}>
                          {option.name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </TableCell>
                <TableCell className={`font-medium ${item.amount < 0 ? "text-red-600" : "text-emerald-600"}`}>
                  {Number(item.amount).toLocaleString(undefined, { style: "currency", currency: "USD" })}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>

      {message ? <p className="mt-3 text-sm text-slate-700">{message}</p> : null}
    </div>
  );
}
