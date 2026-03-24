"""Shared helpers for import hashing and money parsing (CSV + bank presets)."""

from __future__ import annotations

import hashlib
import re
from datetime import date
from decimal import Decimal, InvalidOperation

import pandas as pd


def compute_import_hash(d: date, description: str, amount: Decimal) -> str:
    h = f"{d.isoformat()}|{description.lower()}|{amount}"
    return hashlib.sha256(h.encode("utf-8")).hexdigest()


_MONEY_NOISE = re.compile(r"[^\d.\-+]")


def _clean_money(raw: str) -> str:
    """Strip currency symbols, spaces, commas, and other non-numeric noise."""
    s = raw.strip()
    negative = s.startswith("(") and s.endswith(")")
    s = s.strip("()")
    s = _MONEY_NOISE.sub("", s)
    if negative and s and not s.startswith("-"):
        s = "-" + s
    return s


def amount_from_withdrawals_deposits(withdrawals: object, deposits: object) -> Decimal:
    """Subtract withdrawals (debits), add deposits (credits)."""
    amount = Decimal("0")
    if withdrawals is not None and not pd.isna(withdrawals):
        w = _clean_money(str(withdrawals))
        if w and w.lower() not in ("nan", "null", ""):
            try:
                amount -= Decimal(w)
            except (ValueError, TypeError, InvalidOperation):
                pass
    if deposits is not None and not pd.isna(deposits):
        c = _clean_money(str(deposits))
        if c and c.lower() not in ("nan", "null", ""):
            try:
                amount += Decimal(c)
            except (ValueError, TypeError, InvalidOperation):
                pass
    return amount


def parse_signed_amount_cell(value: object) -> Decimal | None:
    """Parse a single signed amount cell; returns None if empty or invalid."""
    if pd.isna(value):
        return None
    s = _clean_money(str(value))
    if not s or s.lower() in ("", "nan", "null"):
        return None
    try:
        return Decimal(s)
    except (ValueError, TypeError, InvalidOperation):
        return None
