"use client";

import { ChangeEvent, useState } from "react";

import { api } from "@/lib/api";

interface CSVUploadProps {
  onImported: () => Promise<void>;
}

export function CSVUpload({ onImported }: CSVUploadProps) {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<string>("");

  function onFileChange(event: ChangeEvent<HTMLInputElement>) {
    setFile(event.target.files?.[0] ?? null);
  }

  async function handleUpload() {
    if (!file) {
      return;
    }

    setLoading(true);
    setMessage("");
    try {
      const result = await api.uploadCsv(file);
      setMessage(`Imported ${result.rows_imported} rows, skipped ${result.duplicates_skipped} duplicates.`);
      await onImported();
      setFile(null);
    } catch (error) {
      const messageText = error instanceof Error ? error.message : "Upload failed";
      setMessage(messageText);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
      <h2 className="text-lg font-semibold text-slate-900">Import CSV statements</h2>
      <p className="mt-1 text-sm text-slate-600">Upload bank or credit card CSV to merge transactions.</p>
      <div className="mt-4 flex flex-wrap items-center gap-3">
        <input
          type="file"
          accept=".csv"
          onChange={onFileChange}
          className="rounded-lg border border-slate-300 px-3 py-2 text-sm"
        />
        <button
          type="button"
          onClick={handleUpload}
          disabled={loading || !file}
          className="rounded-lg bg-sky-500 px-4 py-2 text-sm font-medium text-white disabled:opacity-50"
        >
          {loading ? "Importing..." : "Import CSV"}
        </button>
      </div>
      {message ? <p className="mt-3 text-sm text-slate-700">{message}</p> : null}
    </div>
  );
}
