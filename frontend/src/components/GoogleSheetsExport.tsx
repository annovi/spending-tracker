"use client";

import { useEffect, useState } from "react";

import { api } from "@/lib/api";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

export function GoogleSheetsExport() {
  const [configured, setConfigured] = useState<boolean | null>(null);
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);

  const [exportSheetId, setExportSheetId] = useState("");
  const [exportWorksheet, setExportWorksheet] = useState("Transactions");
  const [exportDateFrom, setExportDateFrom] = useState("");
  const [exportDateTo, setExportDateTo] = useState("");

  useEffect(() => {
    api
      .googleSheetsStatus()
      .then((s) => setConfigured(s.configured))
      .catch(() => setConfigured(false));
  }, []);

  const runExport = async () => {
    const sid = exportSheetId.trim();
    const ws = exportWorksheet.trim();
    if (!sid || !ws) {
      setMessage("Spreadsheet ID and worksheet name are required for export.");
      return;
    }
    setLoading(true);
    setMessage("");
    try {
      const result = await api.exportGoogleSheet({
        spreadsheet_id: sid,
        worksheet_name: ws,
        date_from: exportDateFrom || undefined,
        date_to: exportDateTo || undefined,
      });
      setMessage(`Exported ${result.rows_written} rows to Google Sheets.`);
    } catch (e) {
      setMessage(e instanceof Error ? e.message : "Export failed");
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
          <CardTitle>Google Sheets export</CardTitle>
          <CardDescription>
            Write Date, Description, Category, Withdrawals, Deposits, Balance, Source to a tab. Creates the tab if
            missing. Share the spreadsheet with your service account.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {!configured ? (
            <Alert>
              <AlertDescription>
                Google Sheets is not configured. Set <code className="text-xs">GOOGLE_SERVICE_ACCOUNT_JSON</code> on
                the backend and share your spreadsheet with the service account email.
              </AlertDescription>
            </Alert>
          ) : (
            <div className="space-y-4 rounded-lg border border-border/60 p-4">
              <div className="grid gap-2">
                <Label>Spreadsheet ID</Label>
                <Input
                  value={exportSheetId}
                  onChange={(e) => setExportSheetId(e.target.value)}
                  placeholder="/d/SPREADSHEET_ID/"
                />
              </div>
              <div className="grid gap-2">
                <Label>Worksheet tab name</Label>
                <Input value={exportWorksheet} onChange={(e) => setExportWorksheet(e.target.value)} />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="grid gap-2">
                  <Label>From date (optional)</Label>
                  <Input type="date" value={exportDateFrom} onChange={(e) => setExportDateFrom(e.target.value)} />
                </div>
                <div className="grid gap-2">
                  <Label>To date (optional)</Label>
                  <Input type="date" value={exportDateTo} onChange={(e) => setExportDateTo(e.target.value)} />
                </div>
              </div>
              <Button type="button" variant="secondary" onClick={runExport} disabled={loading}>
                {loading ? "Working…" : "Export to sheet"}
              </Button>
            </div>
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
