from __future__ import annotations

import json

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas.csv_import import ColumnMapping, CsvPreview
from ..services.bank_parsers import BankPreset, list_bank_presets, parse_bank_csv
from ..services.csv_parser_v2 import detect_columns, parse_transactions_csv_with_mapping
from ..services.import_batch import import_parsed_transactions

router = APIRouter(prefix="/imports", tags=["imports"])


@router.get("/bank-presets")
def get_bank_presets():
    """Supported bank CSV formats for preset import."""
    return {"presets": list_bank_presets()}


@router.post("/csv/preview")
async def preview_csv(
    file: UploadFile = File(...),
):
    """Preview CSV file and detect column mappings"""
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported")

    file_bytes = await file.read()

    import pandas as pd

    df = pd.read_csv(pd.io.common.BytesIO(file_bytes), nrows=5)

    sample_rows = []
    for _, row in df.iterrows():
        row_dict = {}
        for col in df.columns:
            val = row[col]
            if pd.isna(val):
                row_dict[col] = ""
            else:
                row_dict[col] = str(val)[:100]
        sample_rows.append(row_dict)

    detected_mapping = detect_columns(df)

    return CsvPreview(
        columns=list(df.columns),
        sample_rows=sample_rows,
        detected_mapping=detected_mapping,
    )


@router.post("/csv")
async def import_csv(
    file: UploadFile = File(...),
    account_id: int | None = Form(default=None),
    db: Session = Depends(get_db),
):
    """Import CSV with auto-detected columns (legacy endpoint)"""
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported")

    file_bytes = await file.read()
    parsed, _ = parse_transactions_csv_with_mapping(file_bytes, mapping=None)

    return import_parsed_transactions(db, parsed, file.filename, account_id)


@router.post("/csv/with-mapping")
async def import_csv_with_mapping(
    file: UploadFile = File(...),
    account_id: int | None = Form(default=None),
    mapping: str = Form(...),
    db: Session = Depends(get_db),
):
    """Import CSV with explicit column mapping"""
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported")

    file_bytes = await file.read()

    try:
        mapping_dict = json.loads(mapping)
        column_mapping = ColumnMapping(**mapping_dict)
    except (json.JSONDecodeError, TypeError) as e:
        raise HTTPException(status_code=400, detail=f"Invalid mapping format: {str(e)}")

    parsed, _ = parse_transactions_csv_with_mapping(file_bytes, column_mapping)

    return import_parsed_transactions(db, parsed, file.filename, account_id)


@router.post("/csv/bank")
async def import_csv_bank_preset(
    file: UploadFile = File(...),
    bank_preset: str = Form(...),
    account_id: int | None = Form(default=None),
    db: Session = Depends(get_db),
):
    """Import CSV using a bank-specific parser (TD Visa, Scotia, Amex)."""
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported")

    try:
        preset = BankPreset(bank_preset)
    except ValueError:
        valid = ", ".join(p.value for p in BankPreset)
        raise HTTPException(
            status_code=400,
            detail=f"Invalid bank_preset. Use one of: {valid}",
        )

    file_bytes = await file.read()
    try:
        parsed = parse_bank_csv(file_bytes, preset)
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to parse CSV for this bank format: {e!s}",
        )

    return import_parsed_transactions(db, parsed, file.filename, account_id)
