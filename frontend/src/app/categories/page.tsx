import { CategoryManager } from "@/components/CategoryManager";

export default function CategoriesPage() {
  return (
    <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-foreground">Categories</h1>
        <p className="mt-2 text-muted-foreground">
          Create and manage categories to organize your transactions
        </p>
      </div>
      <CategoryManager />
    </main>
  );
}
