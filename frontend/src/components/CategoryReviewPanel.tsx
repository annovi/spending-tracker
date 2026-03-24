"use client";

import { useEffect, useMemo, useState } from "react";

import { SectionPanel } from "@/components/SectionPanel";
import { api } from "@/lib/api";
import type { DateRangeParams } from "@/lib/dashboard-period";
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
  dateRange?: DateRangeParams;
  onSuggestionsChange?: (next: RecategorizationSuggestion[]) => void;
}

export function CategoryReviewPanel({
  suggestions,
  categories,
  onApplied,
  dateRange,
  onSuggestionsChange,
}: CategoryReviewPanelProps) {
  const [localSuggestions, setLocalSuggestions] = useState<RecategorizationSuggestion[]>(suggestions);
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
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

  async function refreshSuggestions() {
    setRefreshing(true);
    setMessage("");
    try {
      const next = await api.listRecategorizationSuggestions(dateRange, true);
      onSuggestionsChange?.(next);
      setLocalSuggestions(next);
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Failed to refresh suggestions");
    } finally {
      setRefreshing(false);
    }
  }

  function changeSuggestedCategory(transactionId: number, nextCategoryId: number) {
    setLocalSuggestions((current) =>
      current.map((item) =>
        item.transaction_id === transactionId
          ? {
              ...item,
              suggested_category_id: nextCategoryId,
              suggested_category_name:
                categoryOptions.find((option) => option.id === nextCategoryId)?.name ??
                item.suggested_category_name,
            }
          : item,
      ),
    );
  }

  const refreshButton = (
    <Button type="button" variant="outline" size="sm" onClick={refreshSuggestions} disabled={refreshing}>
      {refreshing ? "Refreshing…" : "Refresh (re-run AI / rules)"}
    </Button>
  );

  if (!localSuggestions.length) {
    return (
      <SectionPanel
        title="Category Review"
        description="Suggestions are saved in the database after the first load, so the page stays fast. Use refresh only when you want new AI or rule matches."
        actions={onSuggestionsChange ? refreshButton : undefined}
      >
        <p className="mt-2 text-sm text-muted-foreground">No recategorization suggestions right now.</p>
      </SectionPanel>
    );
  }

  return (
    <SectionPanel
      title="Category Review"
      description="Cached suggestions load instantly. Refresh to re-run AI or rules on unreviewed transactions."
      actions={
        <div className="flex flex-wrap items-center gap-2">
          {onSuggestionsChange ? refreshButton : null}
          <Button onClick={applyAll} disabled={loading || !pendingItems.length}>
            {loading ? "Applying..." : `Apply ${pendingItems.length} Suggestions`}
          </Button>
        </div>
      }
    >
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
                <TableCell className="text-muted-foreground">{item.date}</TableCell>
                <TableCell className="text-foreground">{item.description}</TableCell>
                <TableCell className="text-muted-foreground">{item.current_category_name ?? "Uncategorized"}</TableCell>
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
                <TableCell
                  className={`font-medium ${item.amount < 0 ? "text-red-400" : "text-emerald-400"}`}
                >
                  {Number(item.amount).toLocaleString("en-CA", { style: "currency", currency: "CAD" })}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>

      {message ? <p className="mt-3 text-sm text-muted-foreground">{message}</p> : null}
    </SectionPanel>
  );
}
