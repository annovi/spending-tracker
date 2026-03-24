"use client";

import { useRouter } from "next/navigation";

import { CSVUploadAdvanced } from "@/components/CSVUploadAdvanced";
import { GoogleSheetsImport } from "@/components/GoogleSheetsImport";

export default function ImportPage() {
  const router = useRouter();

  const afterImport = async () => {
    router.push("/");
  };

  return (
    <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-foreground">Import data</h1>
        <p className="mt-2 text-muted-foreground">
          Upload CSV files or pull from Google Sheets. After a successful import you can open the dashboard to review
          transactions.
        </p>
      </div>

      <div className="space-y-8">
        <CSVUploadAdvanced onImported={afterImport} />
        <GoogleSheetsImport onImported={afterImport} />
      </div>
    </main>
  );
}
