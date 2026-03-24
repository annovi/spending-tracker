"""Google Drive / Sheets import and export (service account)."""

from __future__ import annotations

import io
import json
from dataclasses import replace
from datetime import date
from typing import Any

import gspread
import pandas as pd
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from gspread.exceptions import WorksheetNotFound
from sqlalchemy.orm import Session, joinedload

from ..config import settings
from ..models import Transaction
from ..schemas.csv_import import ColumnMapping
from .csv_parser_v2 import ParsedTransaction, detect_columns, parse_transactions_csv_with_mapping


def google_sheets_configured() -> bool:
    return bool(settings.google_service_account_json.strip())


def default_folder_configured() -> bool:
    return bool(settings.google_drive_folder_id.strip())


def _raw_credentials() -> str:
    return settings.google_service_account_json.strip()


def _drive_credentials() -> Credentials | None:
    raw = _raw_credentials()
    if not raw:
        return None
    scopes = ["https://www.googleapis.com/auth/drive.readonly"]
    if raw.startswith("{"):
        return Credentials.from_service_account_info(json.loads(raw), scopes=scopes)
    return Credentials.from_service_account_file(raw, scopes=scopes)


def get_gspread_client() -> gspread.Client | None:
    raw = _raw_credentials()
    if not raw:
        return None
    if raw.startswith("{"):
        return gspread.service_account_from_dict(json.loads(raw))
    return gspread.service_account(filename=raw)


def list_worksheets(spreadsheet_id: str) -> list[dict[str, str]]:
    gc = get_gspread_client()
    if not gc:
        raise ValueError("Google credentials not configured")
    sh = gc.open_by_key(spreadsheet_id)
    return [{"title": ws.title, "row_count": ws.row_count} for ws in sh.worksheets()]


def list_spreadsheets_in_folder(folder_id: str) -> list[dict[str, str]]:
    creds = _drive_credentials()
    if not creds:
        raise ValueError("Google credentials not configured")
    service = build("drive", "v3", credentials=creds)
    results: dict[str, Any] = (
        service.files()
        .list(
            q=f"'{folder_id}' in parents and mimeType='application/vnd.google-apps.spreadsheet'",
            pageSize=1000,
            fields="files(id, name)",
        )
        .execute()
    )
    files = results.get("files", [])
    return [{"id": f["id"], "name": f["name"]} for f in files]


def _dedupe_headers(headers: list[str]) -> list[str]:
    seen: dict[str, int] = {}
    result: list[str] = []
    for h in headers:
        key = h.strip()
        if key in seen:
            seen[key] += 1
            result.append(f"{key}_{seen[key]}")
        else:
            seen[key] = 0
            result.append(key)
    return result


_HEADER_KEYWORDS = {
    "date", "description", "amount", "withdrawals", "deposits",
    "debit", "credit", "withdrawal", "deposit", "memo", "details",
    "transaction", "transaction date", "posting date", "source",
}


def _find_header_row(rows: list[list[str]]) -> int:
    """Return the index of the row that looks like a header (contains known column names).

    Scans up to the first 10 rows. Falls back to 0 if nothing matches.
    """
    for idx, row in enumerate(rows[:10]):
        lower_cells = {c.strip().lower() for c in row if c.strip()}
        if lower_cells & _HEADER_KEYWORDS:
            return idx
    return 0


def spreadsheet_rows_to_parsed(
    spreadsheet_id: str,
    worksheet_name: str | None,
) -> list[ParsedTransaction]:
    gc = get_gspread_client()
    if not gc:
        raise ValueError("Google credentials not configured")
    sh = gc.open_by_key(spreadsheet_id)
    ws = sh.worksheet(worksheet_name) if worksheet_name else sh.sheet1
    rows = ws.get_all_values()
    if len(rows) < 2:
        return []
    header_idx = _find_header_row(rows)
    headers = _dedupe_headers(rows[header_idx])
    data_rows = rows[header_idx + 1:]
    padded: list[list[str]] = []
    for r in data_rows:
        row = list(r) + [""] * max(0, len(headers) - len(r))
        padded.append(row[: len(headers)])
    df = pd.DataFrame(padded, columns=headers)
    buf = io.StringIO()
    df.to_csv(buf, index=False)
    file_bytes = buf.getvalue().encode("utf-8")

    mapping: ColumnMapping | None = None
    account_col = "Source" if "Source" in df.columns else None
    if "Date" in df.columns and "Description" in df.columns:
        if "Withdrawals" in df.columns and "Deposits" in df.columns:
            mapping = ColumnMapping(
                date="Date",
                description="Description",
                debit="Withdrawals",
                credit="Deposits",
                account_name=account_col,
            )
        elif "Amount" in df.columns:
            mapping = ColumnMapping(
                date="Date",
                description="Description",
                amount="Amount",
                account_name=account_col,
            )
    if mapping is None:
        mapping = detect_columns(df)
    parsed, _ = parse_transactions_csv_with_mapping(file_bytes, mapping)
    return [replace(p, source="google_sheet") for p in parsed]


def export_transactions_to_sheet(
    db: Session,
    spreadsheet_id: str,
    worksheet_name: str,
    date_from: date | None = None,
    date_to: date | None = None,
) -> int:
    gc = get_gspread_client()
    if not gc:
        raise ValueError("Google credentials not configured")
    sh = gc.open_by_key(spreadsheet_id)
    try:
        ws = sh.worksheet(worksheet_name)
    except WorksheetNotFound:
        ws = sh.add_worksheet(title=worksheet_name, rows="2000", cols="20")

    q = db.query(Transaction).options(joinedload(Transaction.category)).order_by(Transaction.date)
    if date_from is not None:
        q = q.filter(Transaction.date >= date_from)
    if date_to is not None:
        q = q.filter(Transaction.date <= date_to)
    txs = q.all()

    records: list[dict[str, str]] = []
    for t in txs:
        cat = t.category.name if t.category else ""
        amt = t.amount
        if amt < 0:
            w, dep = str(abs(amt)), ""
        else:
            w, dep = "", str(amt)
        records.append(
            {
                "Date": t.date.isoformat(),
                "Description": t.description,
                "Category": cat,
                "Withdrawals": w,
                "Deposits": dep,
                "Balance": "",
                "Source": t.source or "",
            }
        )
    df = pd.DataFrame(records)
    if df.empty:
        df = pd.DataFrame(
            columns=["Date", "Description", "Category", "Withdrawals", "Deposits", "Balance", "Source"]
        )

    values = [df.columns.tolist()] + df.astype(object).where(pd.notna(df), "").values.tolist()
    ws.clear()
    ws.update(values, range_name="A1", value_input_option="USER_ENTERED")
    return len(records)
