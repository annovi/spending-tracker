"use client";

import { ChangeEvent, FocusEvent, useMemo } from "react";

import { api } from "@/lib/api";
import { Category, Transaction } from "@/types";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
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
      <div className="mt-4">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Date</TableHead>
              <TableHead>Description</TableHead>
              <TableHead>Amount</TableHead>
              <TableHead>Category</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {transactions.map((transaction) => (
              <TableRow key={transaction.id}>
                <TableCell className="text-slate-600">{transaction.date}</TableCell>
                <TableCell>
                  <Input
                    defaultValue={transaction.display_name ?? transaction.description}
                    onBlur={(event: FocusEvent<HTMLInputElement>) => {
                      const value = event.target.value.trim();
                      if (value && value !== transaction.display_name) {
                        void updateDescription(transaction, value);
                      }
                    }}
                    className="w-72"
                  />
                </TableCell>
                <TableCell className={`font-medium ${Number(transaction.amount) < 0 ? "text-red-600" : "text-emerald-600"}`}>
                  {Number(transaction.amount).toLocaleString(undefined, {
                    style: "currency",
                    currency: "USD",
                  })}
                </TableCell>
                <TableCell>
                  <div className="flex items-center gap-2">
                    <Select
                      value={transaction.category_id?.toString() ?? "uncategorized"}
                      onValueChange={(value) => {
                        if (value && value !== "uncategorized") {
                          void updateCategory(transaction, Number(value));
                        } else if (value === "uncategorized") {
                          void updateCategory(transaction, null);
                        }
                      }}
                    >
                      <SelectTrigger className="w-[180px]">
                        <SelectValue placeholder="Uncategorized" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="uncategorized">Uncategorized</SelectItem>
                        {categories.map((category) => (
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
                        style={{ backgroundColor: categoryMap.get(transaction.category_id)?.color ?? "#94a3b8" }}
                      />
                    ) : null}
                  </div>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}
