"use client";

import { useState, useEffect } from "react";

import { api } from "@/lib/api";
import { Account } from "@/types";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";

interface AccountFormData {
  name: string;
  type: "bank" | "credit_card" | "cash";
}

export function AccountManager() {
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [loading, setLoading] = useState(true);
  const [editingAccount, setEditingAccount] = useState<Account | null>(null);
  const [formData, setFormData] = useState<AccountFormData>({
    name: "",
    type: "bank",
  });

  const loadAccounts = async () => {
    try {
      const accs = await api.listAccounts();
      setAccounts(accs);
    } catch (error) {
      console.error("Failed to load accounts:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAccounts();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (editingAccount) {
        await api.updateAccount(editingAccount.id, formData);
      } else {
        await api.createAccount(formData);
      }
      await loadAccounts();
      resetForm();
    } catch (error) {
      console.error("Failed to save account:", error);
    }
  };

  const resetForm = () => {
    setFormData({ name: "", type: "bank" });
    setEditingAccount(null);
  };

  const handleEdit = (account: Account) => {
    setEditingAccount(account);
    setFormData({
      name: account.name,
      type: account.type,
    });
  };

  const handleDelete = async (id: number) => {
    if (confirm("Are you sure you want to delete this account? This may affect existing transactions.")) {
      try {
        await api.deleteAccount(id);
        await loadAccounts();
      } catch (error) {
        console.error("Failed to delete account:", error);
      }
    }
  };

  const getAccountTypeLabel = (type: string) => {
    switch (type) {
      case "bank":
        return "Bank Account";
      case "credit_card":
        return "Credit Card";
      case "cash":
        return "Cash";
      default:
        return type;
    }
  };

  const getAccountTypeBadgeVariant = (type: string) => {
    switch (type) {
      case "bank":
        return "default";
      case "credit_card":
        return "secondary";
      case "cash":
        return "outline";
      default:
        return "default";
    }
  };

  if (loading) {
    return <div>Loading accounts...</div>;
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>{editingAccount ? "Edit Account" : "Create New Account"}</CardTitle>
          <CardDescription>
            {editingAccount ? "Update the account details" : "Add a new account to track your transactions"}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="name">Account Name</Label>
                <Input
                  id="name"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  placeholder="e.g., Chase Checking"
                  required
                />
              </div>
              <div>
                <Label htmlFor="type">Account Type</Label>
                <Select
                  value={formData.type}
                  onValueChange={(value: "bank" | "credit_card" | "cash") => setFormData({ ...formData, type: value })}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="bank">Bank Account</SelectItem>
                    <SelectItem value="credit_card">Credit Card</SelectItem>
                    <SelectItem value="cash">Cash</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
            <div className="flex gap-2">
              <Button type="submit">
                {editingAccount ? "Update Account" : "Create Account"}
              </Button>
              {editingAccount && (
                <Button type="button" variant="outline" onClick={resetForm}>
                  Cancel
                </Button>
              )}
            </div>
          </form>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Accounts</CardTitle>
          <CardDescription>Manage your existing accounts</CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Name</TableHead>
                <TableHead>Type</TableHead>
                <TableHead>Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {accounts.map((account) => (
                <TableRow key={account.id}>
                  <TableCell className="font-medium">{account.name}</TableCell>
                  <TableCell>
                    <Badge variant={getAccountTypeBadgeVariant(account.type)}>
                      {getAccountTypeLabel(account.type)}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <div className="flex gap-2">
                      <Button size="sm" variant="outline" onClick={() => handleEdit(account)}>
                        Edit
                      </Button>
                      <Button size="sm" variant="destructive" onClick={() => handleDelete(account.id)}>
                        Delete
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
          {accounts.length === 0 && (
            <div className="text-center py-8 text-slate-500">
              No accounts yet. Create your first account to start tracking transactions.
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
