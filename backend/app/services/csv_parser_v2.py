from __future__ import annotations

import calendar
from dataclasses import dataclass
from datetime import date as date_type, datetime
from decimal import Decimal
from typing import Optional

import pandas as pd

from ..schemas.csv_import import ColumnMapping
from .import_parse_utils import compute_import_hash, amount_from_withdrawals_deposits, parse_signed_amount_cell


@dataclass
class ParsedTransaction:
    date: datetime.date
    description: str
    amount: Decimal
    import_hash: str
    source: str = "csv_import"
    account_name: str | None = None


def detect_columns(df: pd.DataFrame) -> ColumnMapping:
    """Attempt to auto-detect column mappings"""
    lowered = {col.strip().lower(): col for col in df.columns}

    mapping = ColumnMapping()

    for candidate in ["date", "transaction date", "posted date", "time"]:
        if candidate.lower() in lowered:
            mapping.date = lowered[candidate.lower()]
            break

    for candidate in ["description", "memo", "details", "merchant", "payee", "transaction description"]:
        if candidate.lower() in lowered:
            mapping.description = lowered[candidate.lower()]
            break

    for candidate in ["amount", "transaction amount", "value", "sum"]:
        if candidate.lower() in lowered:
            mapping.amount = lowered[candidate.lower()]
            break

    for candidate in ["debit", "withdrawal", "withdrawals", "outflow", "money out"]:
        if candidate.lower() in lowered:
            mapping.debit = lowered[candidate.lower()]
            break

    for candidate in ["credit", "deposit", "deposits", "inflow", "money in"]:
        if candidate.lower() in lowered:
            mapping.credit = lowered[candidate.lower()]
            break

    for candidate in ["source", "bank", "account", "origin"]:
        if candidate.lower() in lowered:
            mapping.account_name = lowered[candidate.lower()]
            break

    return mapping


def parse_transactions_csv_with_mapping(
    file_bytes: bytes,
    mapping: Optional[ColumnMapping] = None,
) -> tuple[list[ParsedTransaction], ColumnMapping]:
    """Parse CSV with provided or auto-detected column mapping"""
    df = pd.read_csv(pd.io.common.BytesIO(file_bytes))

    if not mapping:
        mapping = detect_columns(df)

    if not mapping.date or not mapping.description:
        raise ValueError("CSV must have date and description columns")

    if not mapping.amount and not (mapping.debit or mapping.credit):
        raise ValueError("CSV must have an amount column or both debit and credit columns")

    all_dates = pd.to_datetime(df[mapping.date], errors="coerce").dropna()
    if not all_dates.empty:
        last_valid = all_dates.iloc[-1].date()
        last_day = last_valid.replace(day=calendar.monthrange(last_valid.year, last_valid.month)[1])
        fallback_date: date_type = last_day
    else:
        today = datetime.now().date()
        fallback_date = today.replace(day=calendar.monthrange(today.year, today.month)[1])

    parsed: list[ParsedTransaction] = []
    prev_date: date_type = fallback_date

    for _, row in df.iterrows():
        date_val = pd.to_datetime(row[mapping.date], errors="coerce")
        if pd.isna(date_val):
            d = prev_date
        else:
            d = date_val.date()
            prev_date = d

        description = str(row[mapping.description]).strip() if not pd.isna(row[mapping.description]) else ""
        if not description:
            continue

        if mapping.amount:
            amount = parse_signed_amount_cell(row[mapping.amount])
            if amount is None:
                continue
        else:
            debit_val = row[mapping.debit] if mapping.debit else None
            credit_val = row[mapping.credit] if mapping.credit else None
            amount = amount_from_withdrawals_deposits(debit_val, credit_val)

        if amount == 0:
            continue

        import_hash = compute_import_hash(d, description, amount)

        acct_name: str | None = None
        if mapping.account_name and mapping.account_name in row.index and not pd.isna(row[mapping.account_name]):
            val = str(row[mapping.account_name]).strip()
            if val:
                acct_name = val

        parsed.append(
            ParsedTransaction(
                date=d,
                description=description,
                amount=amount,
                import_hash=import_hash,
                account_name=acct_name,
            )
        )

    return parsed, mapping
