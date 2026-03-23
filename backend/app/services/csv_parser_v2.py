from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
import hashlib
from typing import Optional

import pandas as pd


@dataclass
class ColumnMapping:
    date: Optional[str] = None
    description: Optional[str] = None
    amount: Optional[str] = None
    debit: Optional[str] = None
    credit: Optional[str] = None


@dataclass
class ParsedTransaction:
    date: datetime.date
    description: str
    amount: Decimal
    import_hash: str


def detect_columns(df: pd.DataFrame) -> ColumnMapping:
    """Attempt to auto-detect column mappings"""
    lowered = {col.strip().lower(): col for col in df.columns}
    
    mapping = ColumnMapping()
    
    # Date column candidates
    for candidate in ["date", "transaction date", "posted date", "transaction date", "time"]:
        if candidate.lower() in lowered:
            mapping.date = lowered[candidate.lower()]
            break
    
    # Description column candidates
    for candidate in ["description", "memo", "details", "merchant", "payee", "transaction description"]:
        if candidate.lower() in lowered:
            mapping.description = lowered[candidate.lower()]
            break
    
    # Amount column candidates
    for candidate in ["amount", "transaction amount", "value", "sum"]:
        if candidate.lower() in lowered:
            mapping.amount = lowered[candidate.lower()]
            break
    
    # Debit column candidates
    for candidate in ["debit", "withdrawal", "outflow", "money out"]:
        if candidate.lower() in lowered:
            mapping.debit = lowered[candidate.lower()]
            break
    
    # Credit column candidates
    for candidate in ["credit", "deposit", "inflow", "money in"]:
        if candidate.lower() in lowered:
            mapping.credit = lowered[candidate.lower()]
            break
    
    return mapping


def parse_transactions_csv_with_mapping(
    file_bytes: bytes, 
    mapping: Optional[ColumnMapping] = None
) -> tuple[list[ParsedTransaction], ColumnMapping]:
    """Parse CSV with provided or auto-detected column mapping"""
    df = pd.read_csv(pd.io.common.BytesIO(file_bytes))
    
    # Use provided mapping or auto-detect
    if not mapping:
        mapping = detect_columns(df)
    
    # Validate we have the minimum required columns
    if not mapping.date or not mapping.description:
        raise ValueError("CSV must have date and description columns")
    
    if not mapping.amount and not (mapping.debit or mapping.credit):
        raise ValueError("CSV must have an amount column or both debit and credit columns")
    
    parsed: list[ParsedTransaction] = []
    
    for _, row in df.iterrows():
        # Parse date
        date_val = pd.to_datetime(row[mapping.date], errors="coerce")
        if pd.isna(date_val):
            continue
        
        # Parse description
        description = str(row[mapping.description]).strip() if not pd.isna(row[mapping.description]) else ""
        if not description:
            continue
        
        # Parse amount
        amount = Decimal("0")
        if mapping.amount:
            value = str(row[mapping.amount]).replace(",", "").strip()
            if value and value.lower() not in ["", "nan", "null"]:
                try:
                    amount = Decimal(value)
                except (ValueError, TypeError):
                    continue
        else:
            # Handle separate debit/credit columns
            if mapping.debit and not pd.isna(row[mapping.debit]):
                debit = str(row[mapping.debit]).replace(",", "").strip()
                if debit and debit.lower() not in ["", "nan", "null"]:
                    try:
                        amount -= Decimal(debit)
                    except (ValueError, TypeError):
                        pass
            
            if mapping.credit and not pd.isna(row[mapping.credit]):
                credit = str(row[mapping.credit]).replace(",", "").strip()
                if credit and credit.lower() not in ["", "nan", "null"]:
                    try:
                        amount += Decimal(credit)
                    except (ValueError, TypeError):
                        pass
        
        # Skip zero amount transactions
        if amount == 0:
            continue
        
        # Create import hash
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
    
    return parsed, mapping
