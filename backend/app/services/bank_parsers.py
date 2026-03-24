"""
Bank-specific CSV parsers (TD Visa, Scotia Visa, Scotia Bank, Amex).
Adapted from finance_parser/main.py — reads bytes and returns ParsedTransaction rows.
"""

from __future__ import annotations

from enum import Enum

import pandas as pd

from .csv_parser_v2 import ParsedTransaction
from .import_parse_utils import amount_from_withdrawals_deposits, compute_import_hash


class BankPreset(str, Enum):
    td_visa = "td_visa"
    scotia_visa = "scotia_visa"
    scotia_bank = "scotia_bank"
    amex = "amex"


def _parse_td_dataframe(df: pd.DataFrame, source: str) -> list[ParsedTransaction]:
    df = df.iloc[:, [0, 1, 2, 3]].copy()
    df.columns = ["Date", "Description", "Withdrawals", "Deposits"]
    df["Date"] = pd.to_datetime(df["Date"], format="%m/%d/%Y", errors="coerce")
    df["Withdrawals"] = pd.to_numeric(df["Withdrawals"], errors="coerce")
    df["Deposits"] = pd.to_numeric(df["Deposits"], errors="coerce")
    return _dataframe_to_parsed(df, source)


def _parse_scotia_style(df: pd.DataFrame, source: str) -> list[ParsedTransaction]:
    df = df.copy()
    if "Sub-description" not in df.columns:
        df["Sub-description"] = ""
    df = df.rename(
        columns={
            "Date": "Date",
            "Description": "Description",
            "Sub-description": "SubDesc",
            "Type of Transaction": "Type",
            "Amount": "Amount",
        }
    )
    df["Date"] = pd.to_datetime(df["Date"], format="%Y-%m-%d", errors="coerce")
    df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce")
    df["Description"] = df["Description"].fillna("") + " " + df["SubDesc"].fillna("")
    df["Description"] = df["Description"].str.strip()
    df["Withdrawals"] = df.apply(
        lambda row: abs(row["Amount"])
        if str(row["Type"]).lower() == "debit" and not pd.isna(row["Amount"])
        else None,
        axis=1,
    )
    df["Deposits"] = df.apply(
        lambda row: abs(row["Amount"])
        if str(row["Type"]).lower() == "credit" and not pd.isna(row["Amount"])
        else None,
        axis=1,
    )
    return _dataframe_to_parsed(df[["Date", "Description", "Withdrawals", "Deposits"]], source)


def _parse_amex_dataframe(df: pd.DataFrame, source: str) -> list[ParsedTransaction]:
    df = df.rename(columns={"Date": "Date", "Description": "Description", "Amount": "Amount"})
    df = df[["Date", "Description", "Amount"]]
    df["Date"] = pd.to_datetime(df["Date"], format="%d %b %Y", errors="coerce")
    df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce")
    df["Withdrawals"] = df["Amount"].apply(lambda x: x if pd.notna(x) and x > 0 else None)
    df["Deposits"] = df["Amount"].apply(
        lambda x: abs(x) if pd.notna(x) and x < 0 else None
    )
    return _dataframe_to_parsed(df.drop(columns=["Amount"]), source)


def _dataframe_to_parsed(df: pd.DataFrame, source: str) -> list[ParsedTransaction]:
    out: list[ParsedTransaction] = []
    for _, row in df.iterrows():
        if pd.isna(row["Date"]):
            continue
        d = pd.Timestamp(row["Date"]).date()
        description = str(row["Description"]).strip() if not pd.isna(row["Description"]) else ""
        if not description:
            continue
        amount = amount_from_withdrawals_deposits(row.get("Withdrawals"), row.get("Deposits"))
        if amount == 0:
            continue
        import_hash = compute_import_hash(d, description, amount)
        out.append(
            ParsedTransaction(
                date=d,
                description=description,
                amount=amount,
                import_hash=import_hash,
                source=source,
            )
        )
    return out


def parse_bank_csv(file_bytes: bytes, preset: BankPreset) -> list[ParsedTransaction]:
    bio = pd.io.common.BytesIO(file_bytes)
    if preset == BankPreset.td_visa:
        df = pd.read_csv(bio, header=0)
        return _parse_td_dataframe(df, BankPreset.td_visa.value)
    if preset in (BankPreset.scotia_visa, BankPreset.scotia_bank):
        df = pd.read_csv(bio, header=0)
        return _parse_scotia_style(df, preset.value)
    if preset == BankPreset.amex:
        df = pd.read_csv(bio)
        return _parse_amex_dataframe(df, BankPreset.amex.value)
    raise ValueError(f"Unknown bank preset: {preset}")


BANK_PRESET_LABELS: list[tuple[str, str]] = [
    (BankPreset.td_visa.value, "TD Visa"),
    (BankPreset.scotia_visa.value, "Scotia Visa"),
    (BankPreset.scotia_bank.value, "Scotia Bank"),
    (BankPreset.amex.value, "American Express"),
]


def list_bank_presets() -> list[dict[str, str]]:
    return [{"id": pid, "label": label} for pid, label in BANK_PRESET_LABELS]
