import { AccountManager } from "@/components/AccountManager";

export default function AccountsPage() {
  return (
    <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-foreground">Accounts</h1>
        <p className="mt-2 text-muted-foreground">
          Create and manage accounts to organize your transactions by bank, credit card, or cash
        </p>
      </div>
      <AccountManager />
    </main>
  );
}
