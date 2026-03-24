"use client";

import { ChangeEvent, useEffect, useState } from "react";

import { AccountSelect } from "@/components/AccountSelect";
import { api, formatImportResult, type CsvColumnMapping, type CsvPreviewResponse } from "@/lib/api";
import { Account } from "@/types";
import { Button } from "@/components/ui/button";
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
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Alert, AlertDescription } from "@/components/ui/alert";

interface CSVUploadProps {
  onImported: () => Promise<void>;
}

export function CSVUploadAdvanced({ onImported }: CSVUploadProps) {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<string>("");
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [selectedAccountId, setSelectedAccountId] = useState<number | undefined>();
  const [bankFormat, setBankFormat] = useState<string>("auto");
  const [showMapping, setShowMapping] = useState(false);
  const [csvPreview, setCsvPreview] = useState<CsvPreviewResponse | null>(null);
  const [columnMapping, setColumnMapping] = useState<CsvColumnMapping>({});
  const [bankOptions, setBankOptions] = useState<{ id: string; label: string }[]>([
    { id: "auto", label: "Auto-detect columns" },
  ]);

  useEffect(() => {
    api.listAccounts().then(setAccounts).catch(console.error);
  }, []);

  useEffect(() => {
    api
      .listBankPresets()
      .then((r) => {
        setBankOptions([{ id: "auto", label: "Auto-detect columns" }, ...r.presets]);
      })
      .catch(console.error);
  }, []);

  const handleBankFormatChange = (value: string) => {
    setBankFormat(value);
    setFile(null);
    setShowMapping(false);
    setCsvPreview(null);
    setColumnMapping({});
    setMessage("");
  };

  const handleFileChange = async (event: ChangeEvent<HTMLInputElement>) => {
    const selectedFile = event.target.files?.[0];
    if (!selectedFile) return;

    setFile(selectedFile);
    setMessage("");
    setShowMapping(false);
    setCsvPreview(null);
    setColumnMapping({});

    if (bankFormat !== "auto") {
      setLoading(true);
      try {
        const result = await api.uploadCsvWithBankPreset(
          selectedFile,
          bankFormat,
          selectedAccountId
        );
        setMessage(formatImportResult(result));
        await onImported();
        setFile(null);
        event.target.value = "";
      } catch (error) {
        const messageText = error instanceof Error ? error.message : "Import failed";
        setMessage(messageText);
      } finally {
        setLoading(false);
      }
      return;
    }

    try {
      setLoading(true);
      const preview = await api.previewCsv(selectedFile);
      setCsvPreview(preview);

      if (preview.detected_mapping) {
        setColumnMapping(preview.detected_mapping);
      }

      setShowMapping(true);
    } catch (error) {
      const messageText = error instanceof Error ? error.message : "Preview failed";
      setMessage(messageText);
      setShowMapping(false);
    } finally {
      setLoading(false);
    }
  };

  const handleImport = async () => {
    if (!file) return;

    setLoading(true);
    setMessage("");

    try {
      const result = await api.uploadCsvWithMapping(
        file,
        columnMapping as Record<string, string>,
        selectedAccountId
      );
      setMessage(formatImportResult(result));
      await onImported();
      setFile(null);
      setShowMapping(false);
      setCsvPreview(null);
      setColumnMapping({});
    } catch (error) {
      const messageText = error instanceof Error ? error.message : "Upload failed";
      setMessage(messageText);
    } finally {
      setLoading(false);
    }
  };

  const handleQuickImport = async () => {
    if (!file) return;

    setLoading(true);
    setMessage("");

    try {
      const result = await api.uploadCsv(file, selectedAccountId);
      setMessage(formatImportResult(result));
      await onImported();
      setFile(null);
      setShowMapping(false);
      setCsvPreview(null);
      setColumnMapping({});
    } catch (error) {
      const messageText = error instanceof Error ? error.message : "Upload failed";
      setMessage(messageText);
    } finally {
      setLoading(false);
    }
  };

  const isMappingValid = () => {
    return columnMapping.date && columnMapping.description &&
      (columnMapping.amount || (columnMapping.debit && columnMapping.credit));
  };

  const selectableColumns = csvPreview
    ? csvPreview.columns.filter((col) => col.trim().length > 0)
    : [];

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle>Import CSV statements</CardTitle>
          <CardDescription>Upload bank or credit card CSV to merge transactions.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-2 max-w-md">
            <Label>Bank CSV format</Label>
            <Select value={bankFormat} onValueChange={handleBankFormatChange}>
              <SelectTrigger>
                <SelectValue placeholder="Choose format" />
              </SelectTrigger>
              <SelectContent>
                {bankOptions.map((opt) => (
                  <SelectItem key={opt.id} value={opt.id}>
                    {opt.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div className="flex flex-wrap items-end gap-3">
            <div>
              <Label className="sr-only">CSV file</Label>
              <Input
                type="file"
                accept=".csv"
                onChange={handleFileChange}
                className="w-fit"
              />
            </div>
            <AccountSelect
              accounts={accounts}
              value={selectedAccountId}
              onChange={setSelectedAccountId}
              triggerClassName="w-[200px]"
            />
            {bankFormat === "auto" && file && !showMapping && (
              <Button onClick={handleQuickImport} disabled={loading}>
                {loading ? "Importing..." : "Quick Import"}
              </Button>
            )}
          </div>

          {file && showMapping && csvPreview && (
            <div className="space-y-4">
              <Alert>
                <AlertDescription>
                  We detected {csvPreview.columns.length} columns. Please map them to import fields.
                </AlertDescription>
              </Alert>

              <div className="grid gap-4">
                <div>
                  <Label>Date Column *</Label>
                  <Select
                    value={columnMapping.date ?? "none"}
                    onValueChange={(value) => setColumnMapping({ ...columnMapping, date: value && value !== "none" ? value : undefined })}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select date column" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="none">None</SelectItem>
                      {selectableColumns.map((col) => (
                        <SelectItem key={col} value={col}>
                          {col}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <Label>Description Column *</Label>
                  <Select
                    value={columnMapping.description ?? "none"}
                    onValueChange={(value) => setColumnMapping({ ...columnMapping, description: value && value !== "none" ? value : undefined })}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select description column" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="none">None</SelectItem>
                      {selectableColumns.map((col) => (
                        <SelectItem key={col} value={col}>
                          {col}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="grid grid-cols-3 gap-4">
                  <div>
                    <Label>Amount Column</Label>
                    <Select
                      value={columnMapping.amount ?? "none"}
                      onValueChange={(value) => {
                        setColumnMapping({
                          ...columnMapping,
                          amount: value && value !== "none" ? value : undefined,
                          debit: value && value !== "none" ? undefined : columnMapping.debit,
                          credit: value && value !== "none" ? undefined : columnMapping.credit
                        });
                      }}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Select amount column" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="none">None</SelectItem>
                        {selectableColumns.map((col) => (
                          <SelectItem key={col} value={col}>
                            {col}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  <div>
                    <Label>Debit Column</Label>
                    <Select
                      value={columnMapping.debit ?? "none"}
                      onValueChange={(value) => setColumnMapping({
                        ...columnMapping,
                        debit: value && value !== "none" ? value : undefined,
                        amount: value && value !== "none" ? undefined : columnMapping.amount
                      })}
                      disabled={!!columnMapping.amount}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Select debit column" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="none">None</SelectItem>
                        {selectableColumns.map((col) => (
                          <SelectItem key={col} value={col}>
                            {col}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  <div>
                    <Label>Credit Column</Label>
                    <Select
                      value={columnMapping.credit ?? "none"}
                      onValueChange={(value) => {
                        setColumnMapping({
                          ...columnMapping,
                          credit: value && value !== "none" ? value : undefined,
                          amount: value && value !== "none" ? undefined : columnMapping.amount
                        });
                      }}
                      disabled={!!columnMapping.amount}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Select credit column" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="none">None</SelectItem>
                        {selectableColumns.map((col) => (
                          <SelectItem key={col} value={col}>
                            {col}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                </div>
              </div>

              <div className="space-y-2">
                <Label>CSV Preview (first 5 rows)</Label>
                <div className="border rounded-md overflow-auto">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        {csvPreview.columns.map((col) => (
                          <TableHead key={col} className="whitespace-nowrap">
                            {col}
                          </TableHead>
                        ))}
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {csvPreview.sample_rows.map((row, idx) => (
                        <TableRow key={idx}>
                          {csvPreview.columns.map((col) => (
                            <TableCell key={col} className="max-w-[200px] truncate">
                              {row[col] || ""}
                            </TableCell>
                          ))}
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </div>
              </div>

              <Button
                onClick={handleImport}
                disabled={loading || !isMappingValid()}
                className="w-full"
              >
                {loading ? "Importing..." : "Import with Column Mapping"}
              </Button>
            </div>
          )}
        </CardContent>
      </Card>

      {message && (
        <Alert>
          <AlertDescription>{message}</AlertDescription>
        </Alert>
      )}
    </div>
  );
}
