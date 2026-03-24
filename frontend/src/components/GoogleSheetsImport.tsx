"use client";

import { useEffect, useState } from "react";

import { AccountSelect } from "@/components/AccountSelect";
import { api, formatImportResult } from "@/lib/api";
import { Account } from "@/types";
import { Alert, AlertDescription } from "@/components/ui/alert";
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

interface GoogleSheetsImportProps {
  onImported?: () => void | Promise<void>;
}

export function GoogleSheetsImport({ onImported }: GoogleSheetsImportProps) {
  const [configured, setConfigured] = useState<boolean | null>(null);
  const [hasDefaultFolder, setHasDefaultFolder] = useState(false);
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);

  const [folderId, setFolderId] = useState("");
  const [spreadsheets, setSpreadsheets] = useState<{ id: string; name: string }[]>([]);
  const [selectedSheetId, setSelectedSheetId] = useState("");
  const [worksheets, setWorksheets] = useState<{ title: string; row_count: number }[]>([]);
  const [importWorksheet, setImportWorksheet] = useState("");
  const [loadingWorksheets, setLoadingWorksheets] = useState(false);
  const [importAccountId, setImportAccountId] = useState<number | undefined>();

  useEffect(() => {
    api
      .googleSheetsStatus()
      .then((s) => {
        setConfigured(s.configured);
        setHasDefaultFolder(s.has_default_folder);
      })
      .catch(() => {
        setConfigured(false);
        setHasDefaultFolder(false);
      });
    api.listAccounts().then(setAccounts).catch(console.error);
  }, []);

  const fetchWorksheets = async (spreadsheetId: string) => {
    if (!spreadsheetId.trim()) {
      setWorksheets([]);
      return;
    }
    setLoadingWorksheets(true);
    try {
      const res = await api.listGoogleWorksheets(spreadsheetId.trim());
      setWorksheets(res.worksheets);
      setImportWorksheet(res.worksheets.length > 0 ? res.worksheets[0].title : "");
    } catch {
      setWorksheets([]);
    } finally {
      setLoadingWorksheets(false);
    }
  };

  const handleSpreadsheetSelect = (sheetId: string) => {
    setSelectedSheetId(sheetId);
    setImportWorksheet("");
    setWorksheets([]);
    void fetchWorksheets(sheetId);
  };

  const listSpreadsheets = async () => {
    setMessage("");
    setLoading(true);
    try {
      const res = await api.listGoogleSpreadsheets(folderId.trim() || undefined);
      setSpreadsheets(res.spreadsheets);
      setMessage(`Found ${res.spreadsheets.length} spreadsheet(s).`);
    } catch (e) {
      setSpreadsheets([]);
      setMessage(e instanceof Error ? e.message : "Failed to list spreadsheets");
    } finally {
      setLoading(false);
    }
  };

  const runImport = async () => {
    const sid = selectedSheetId.trim();
    if (!sid) {
      setMessage("Select or enter a spreadsheet ID.");
      return;
    }
    setLoading(true);
    setMessage("");
    try {
      const result = await api.importGoogleSheet({
        spreadsheet_id: sid,
        worksheet_name: importWorksheet.trim() || undefined,
        account_id: importAccountId,
      });
      setMessage(formatImportResult(result));
      await onImported?.();
    } catch (e) {
      setMessage(e instanceof Error ? e.message : "Import failed");
    } finally {
      setLoading(false);
    }
  };

  if (configured === null) {
    return null;
  }

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle>Google Sheets import</CardTitle>
          <CardDescription>
            Pull transactions from a shared spreadsheet. Requires a Google Cloud service account (see README /
            docs/google-sheets-setup.md).
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {!configured ? (
            <Alert>
              <AlertDescription>
                Google Sheets is not configured. Set <code className="text-xs">GOOGLE_SERVICE_ACCOUNT_JSON</code> on
                the backend and share your spreadsheets with the service account email.
              </AlertDescription>
            </Alert>
          ) : (
            <>
              <p className="text-sm text-muted-foreground">
                Status: connected
                {hasDefaultFolder ? " · default Drive folder ID is set" : ""}
              </p>

              <div className="space-y-4 rounded-lg border border-border/60 p-4">
                <div className="grid gap-2">
                  <Label>Drive folder ID (optional if GOOGLE_DRIVE_FOLDER_ID is set)</Label>
                  <Input
                    value={folderId}
                    onChange={(e) => setFolderId(e.target.value)}
                    placeholder="Folder ID from Drive URL"
                  />
                  <Button type="button" variant="secondary" onClick={listSpreadsheets} disabled={loading}>
                    List spreadsheets in folder
                  </Button>
                </div>
                {spreadsheets.length > 0 ? (
                  <div className="grid gap-2">
                    <Label>Spreadsheet</Label>
                    <Select value={selectedSheetId} onValueChange={handleSpreadsheetSelect}>
                      <SelectTrigger>
                        <SelectValue placeholder="Choose a spreadsheet" />
                      </SelectTrigger>
                      <SelectContent>
                        {spreadsheets.map((s) => (
                          <SelectItem key={s.id} value={s.id}>
                            {s.name}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                ) : null}
                <div className="grid gap-2">
                  <Label>Or paste spreadsheet ID</Label>
                  <div className="flex gap-2">
                    <Input
                      value={selectedSheetId}
                      onChange={(e) => setSelectedSheetId(e.target.value)}
                      placeholder="From URL: /d/SPREADSHEET_ID/"
                      className="flex-1"
                    />
                    <Button
                      type="button"
                      variant="secondary"
                      onClick={() => void fetchWorksheets(selectedSheetId)}
                      disabled={loadingWorksheets || !selectedSheetId.trim()}
                    >
                      {loadingWorksheets ? "Loading…" : "Load tabs"}
                    </Button>
                  </div>
                </div>
                <div className="grid gap-2">
                  <Label>Worksheet tab</Label>
                  {worksheets.length > 0 ? (
                    <Select value={importWorksheet} onValueChange={setImportWorksheet}>
                      <SelectTrigger>
                        <SelectValue placeholder="Choose a worksheet tab" />
                      </SelectTrigger>
                      <SelectContent>
                        {worksheets.map((ws) => (
                          <SelectItem key={ws.title} value={ws.title}>
                            {ws.title} ({ws.row_count} rows)
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  ) : (
                    <Input
                      value={importWorksheet}
                      onChange={(e) => setImportWorksheet(e.target.value)}
                      placeholder={loadingWorksheets ? "Loading tabs…" : "Select a spreadsheet first to see tabs"}
                      disabled={loadingWorksheets}
                    />
                  )}
                </div>
                <div className="grid gap-2">
                  <Label>Account (optional)</Label>
                  <AccountSelect
                    accounts={accounts}
                    value={importAccountId}
                    onChange={setImportAccountId}
                    triggerClassName="w-[240px]"
                    placeholder="No account"
                    noAccountLabel="No account"
                  />
                </div>
                <Button type="button" onClick={runImport} disabled={loading || !selectedSheetId.trim()}>
                  {loading ? "Working…" : "Import from sheet"}
                </Button>
              </div>
            </>
          )}
        </CardContent>
      </Card>
      {message ? (
        <Alert>
          <AlertDescription className="whitespace-pre-wrap break-all">{message}</AlertDescription>
        </Alert>
      ) : null}
    </div>
  );
}
