from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
import hashlib

import pandas as pd


@dataclass
class ParsedTransaction:
    date: datetime.date
    description: str
    amount: Decimal
    import_hash: str


def _pick_column(df: pd.DataFrame, candidates: list[str]) -> str | None:
    lowered = {col.strip().lower(): col for col in df.columns}
    for candidate in candidates:
        key = candidate.lower()
        if key in lowered:
            return lowered[key]
    return None


def parse_transactions_csv(file_bytes: bytes) -> list[ParsedTransaction]:
    df = pd.read_csv(pd.io.common.BytesIO(file_bytes))

    date_col = _pick_column(df, ["date", "transaction date", "posted date"])
    desc_col = _pick_column(df, ["description", "memo", "details", "merchant"])
    amount_col = _pick_column(df, ["amount", "transaction amount", "value"])
    debit_col = _pick_column(df, ["debit", "withdrawal"])
    credit_col = _pick_column(df, ["credit", "deposit"])

    if not date_col or not desc_col or (not amount_col and not (debit_col or credit_col)):
        raise ValueError("CSV missing required columns. Need date, description, and amount (or debit/credit).")

    parsed: list[ParsedTransaction] = []

    for _, row in df.iterrows():
        date_val = pd.to_datetime(row[date_col], errors="coerce")
        if pd.isna(date_val):
            continue

        description = str(row[desc_col]).strip() if not pd.isna(row[desc_col]) else ""
        if not description:
            continue

        amount = Decimal("0")
        if amount_col:
            value = str(row[amount_col]).replace(",", "").strip()
            if value:
                amount = Decimal(value)
        else:
            debit = str(row[debit_col]).replace(",", "").strip() if debit_col and not pd.isna(row[debit_col]) else ""
            credit = str(row[credit_col]).replace(",", "").strip() if credit_col and not pd.isna(row[credit_col]) else ""
            if credit:
                amount += Decimal(credit)
            if debit:
                amount -= Decimal(debit)

        hash_input = f"{date_val.date().isoformat()}|{description.lower()}|{amount}"
        import_hash = hashlib.sha256(hash_input.encode("utf-8")).hexdigest()

        parsed.append(
            ParsedTransaction(
                date=date_val.date(),
                description=description,
                amount=amount,
                import_hash=import_hash,
            )
        )

    return parsed
