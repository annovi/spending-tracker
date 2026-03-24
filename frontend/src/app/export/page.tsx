import { GoogleSheetsExport } from "@/components/GoogleSheetsExport";

export default function ExportPage() {
  return (
    <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-foreground">Export data</h1>
        <p className="mt-2 text-muted-foreground">
          Send your transactions to a Google Sheet. Configure the service account on the backend first.
        </p>
      </div>

      <GoogleSheetsExport />
    </main>
  );
}
