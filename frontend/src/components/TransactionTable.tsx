"use client";

import type { ReactNode } from "react";
import { FocusEvent, useEffect, useMemo, useState } from "react";

import { AccountSelect } from "@/components/AccountSelect";
import { api } from "@/lib/api";
import { Account, Category, Transaction } from "@/types";
import { SectionPanel } from "@/components/SectionPanel";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
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

const COLUMN_ORDER = ["date", "description", "amount", "category", "account", "source"] as const;
type ColumnKey = (typeof COLUMN_ORDER)[number];

const DEFAULT_VISIBLE: Record<ColumnKey, boolean> = {
  date: true,
  description: true,
  amount: true,
  category: true,
  account: false,
  source: false,
};

const COLUMN_LABELS: Record<ColumnKey, string> = {
  date: "Date",
  description: "Description",
  amount: "Amount",
  category: "Category",
  account: "Account",
  source: "Source",
};

const STORAGE_KEY = "spending-tracker-tx-columns-v1";

function loadColumnVisibility(): Record<ColumnKey, boolean> {
  if (typeof window === "undefined") {
    return { ...DEFAULT_VISIBLE };
  }
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) {
      return { ...DEFAULT_VISIBLE };
    }
    const parsed = JSON.parse(raw) as Partial<Record<ColumnKey, boolean>>;
    return { ...DEFAULT_VISIBLE, ...parsed };
  } catch {
    return { ...DEFAULT_VISIBLE };
  }
}

interface TransactionTableProps {
  transactions: Transaction[];
  categories: Category[];
  accounts: Account[];
  onUpdated: () => Promise<void>;
}

export function TransactionTable({ transactions, categories, accounts, onUpdated }: TransactionTableProps) {
  const [columnVisible, setColumnVisible] = useState<Record<ColumnKey, boolean>>(loadColumnVisibility);

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(columnVisible));
  }, [columnVisible]);

  const categoryMap = useMemo(() => {
    return new Map(categories.map((category) => [category.id, category]));
  }, [categories]);

  const visibleColumns = useMemo(
    () => COLUMN_ORDER.filter((k) => columnVisible[k]),
    [columnVisible]
  );

  async function updateDescription(transaction: Transaction, displayName: string) {
    await api.updateTransaction(transaction.id, { display_name: displayName });
    await onUpdated();
  }

  async function updateCategory(transaction: Transaction, categoryId: number | null) {
    await api.updateTransaction(transaction.id, { category_id: categoryId, is_reviewed: true });
    await onUpdated();
  }

  async function updateAccount(transaction: Transaction, accountId: number | undefined) {
    await api.updateTransaction(transaction.id, { account_id: accountId ?? null });
    await onUpdated();
  }

  const columnToggles = (
    <div className="flex flex-wrap items-center gap-x-4 gap-y-2 rounded-lg border border-border/50 bg-muted/30 px-3 py-2 text-xs">
      <span className="font-medium text-muted-foreground">Columns</span>
      {COLUMN_ORDER.map((key) => (
        <label key={key} className="flex cursor-pointer items-center gap-1.5 text-foreground">
          <input
            type="checkbox"
            className="size-3.5 rounded border-border accent-primary"
            checked={columnVisible[key]}
            onChange={(e) => setColumnVisible((prev) => ({ ...prev, [key]: e.target.checked }))}
          />
          {COLUMN_LABELS[key]}
        </label>
      ))}
    </div>
  );

  return (
    <SectionPanel title="Transactions" description="Show or hide columns. Account and Source appear on the right when enabled.">
      <div className="mt-3">{columnToggles}</div>
      <div className="mt-4">
        <Table>
          <TableHeader>
            <TableRow>
              {visibleColumns.map((key) => (
                <TableHead key={key}>{COLUMN_LABELS[key]}</TableHead>
              ))}
            </TableRow>
          </TableHeader>
          <TableBody>
            {transactions.map((transaction) => (
              <TableRow key={transaction.id}>
                {visibleColumns.map((key) => (
                  <TableCell key={key}>{renderCell(key, transaction, { categoryMap, categories, accounts, updateDescription, updateCategory, updateAccount })}</TableCell>
                ))}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </SectionPanel>
  );
}

function renderCell(
  key: ColumnKey,
  transaction: Transaction,
  ctx: {
    categoryMap: Map<number, Category>;
    categories: Category[];
    accounts: Account[];
    updateDescription: (t: Transaction, v: string) => Promise<void>;
    updateCategory: (t: Transaction, id: number | null) => Promise<void>;
    updateAccount: (t: Transaction, id: number | undefined) => Promise<void>;
  }
): ReactNode {
  switch (key) {
    case "date":
      return <span className="text-muted-foreground whitespace-nowrap">{transaction.date}</span>;
    case "description":
      return (
        <Input
          defaultValue={transaction.display_name ?? transaction.description}
          onBlur={(event: FocusEvent<HTMLInputElement>) => {
            const value = event.target.value.trim();
            if (value && value !== transaction.display_name) {
              void ctx.updateDescription(transaction, value);
            }
          }}
          className="min-w-[12rem] max-w-md"
        />
      );
    case "amount":
      return (
        <span className={`font-medium whitespace-nowrap ${Number(transaction.amount) < 0 ? "text-red-400" : "text-emerald-400"}`}>
          {Number(transaction.amount).toLocaleString("en-CA", {
            style: "currency",
            currency: "CAD",
          })}
        </span>
      );
    case "category":
      return (
        <div className="flex items-center gap-2">
          <Select
            value={transaction.category_id?.toString() ?? "uncategorized"}
            onValueChange={(value) => {
              if (value && value !== "uncategorized") {
                void ctx.updateCategory(transaction, Number(value));
              } else if (value === "uncategorized") {
                void ctx.updateCategory(transaction, null);
              }
            }}
          >
            <SelectTrigger className="w-[180px]">
              <SelectValue placeholder="Uncategorized" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="uncategorized">Uncategorized</SelectItem>
              {ctx.categories.map((category) => (
                <SelectItem key={category.id} value={category.id.toString()}>
                  {category.name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          {transaction.category_id ? (
            <Badge
              variant="secondary"
              className="h-2.5 w-2.5 rounded-full p-0"
              style={{ backgroundColor: ctx.categoryMap.get(transaction.category_id)?.color ?? "#94a3b8" }}
            />
          ) : null}
        </div>
      );
    case "account":
      return (
        <AccountSelect
          accounts={ctx.accounts}
          value={transaction.account_id ?? undefined}
          onChange={(id) => void ctx.updateAccount(transaction, id)}
          triggerClassName="w-[200px]"
          placeholder="No account"
          noAccountLabel="No account"
        />
      );
    case "source":
      return <span className="max-w-[10rem] truncate text-muted-foreground text-sm">{transaction.source || "—"}</span>;
    default:
      return null;
  }
}
