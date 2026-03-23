from __future__ import annotations

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session
from typing import Optional

from ..database import get_db
from ..models import Category, ImportLog, Transaction
from ..services.categorizer import suggest_category
from ..services.csv_parser_v2 import parse_transactions_csv_with_mapping, ColumnMapping, detect_columns
from ..schemas.csv_import import CsvPreview, CsvImportRequest, ColumnMapping as ColumnMappingSchema


router = APIRouter(prefix="/imports", tags=["imports"])


@router.post("/csv/preview")
async def preview_csv(
    file: UploadFile = File(...),
):
    """Preview CSV file and detect column mappings"""
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported")

    file_bytes = await file.read()
    
    # Read first few rows for preview
    import pandas as pd
    df = pd.read_csv(pd.io.common.BytesIO(file_bytes), nrows=5)
    
    # Convert to dict for JSON response
    sample_rows = []
    for _, row in df.iterrows():
        row_dict = {}
        for col in df.columns:
            val = row[col]
            if pd.isna(val):
                row_dict[col] = ""
            else:
                row_dict[col] = str(val)[:100]  # Limit preview length
        sample_rows.append(row_dict)
    
    # Detect column mapping
    detected_mapping = detect_columns(df)
    
    return CsvPreview(
        columns=list(df.columns),
        sample_rows=sample_rows,
        detected_mapping=ColumnMappingSchema(
            date=detected_mapping.date,
            description=detected_mapping.description,
            amount=detected_mapping.amount,
            debit=detected_mapping.debit,
            credit=detected_mapping.credit
        )
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

    categories = db.query(Category).all()
    category_names = [c.name for c in categories]
    category_map = {c.name: c.id for c in categories}

    imported = 0
    duplicates = 0

    for item in parsed:
        existing = db.query(Transaction).filter(Transaction.import_hash == item.import_hash).first()
        if existing:
            duplicates += 1
            continue

        suggested_category_name = suggest_category(item.description, category_names, db)
        suggested_category_id = category_map.get(suggested_category_name) if suggested_category_name else None

        transaction = Transaction(
            date=item.date,
            description=item.description,
            amount=item.amount,
            account_id=account_id,
            category_id=suggested_category_id,
            source="csv_import",
            import_hash=item.import_hash,
            is_reviewed=False,
        )
        db.add(transaction)
        imported += 1

    db.add(
        ImportLog(
            filename=file.filename,
            account_id=account_id,
            rows_imported=imported,
            duplicates_skipped=duplicates,
        )
    )
    db.commit()

    return {"rows_imported": imported, "duplicates_skipped": duplicates}


@router.post("/csv/with-mapping")
async def import_csv_with_mapping(
    file: UploadFile = File(...),
    account_id: int | None = Form(default=None),
    mapping: str = Form(...),  # JSON string of ColumnMapping
    db: Session = Depends(get_db),
):
    """Import CSV with explicit column mapping"""
    import json
    
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported")

    file_bytes = await file.read()
    
    # Parse mapping from JSON
    try:
        mapping_dict = json.loads(mapping)
        column_mapping = ColumnMapping(**mapping_dict)
    except (json.JSONDecodeError, TypeError) as e:
        raise HTTPException(status_code=400, detail=f"Invalid mapping format: {str(e)}")
    
    # Parse with mapping
    parsed, _ = parse_transactions_csv_with_mapping(file_bytes, column_mapping)

    categories = db.query(Category).all()
    category_names = [c.name for c in categories]
    category_map = {c.name: c.id for c in categories}

    imported = 0
    duplicates = 0

    for item in parsed:
        existing = db.query(Transaction).filter(Transaction.import_hash == item.import_hash).first()
        if existing:
            duplicates += 1
            continue

        suggested_category_name = suggest_category(item.description, category_names, db)
        suggested_category_id = category_map.get(suggested_category_name) if suggested_category_name else None

        transaction = Transaction(
            date=item.date,
            description=item.description,
            amount=item.amount,
            account_id=account_id,
            category_id=suggested_category_id,
            source="csv_import",
            import_hash=item.import_hash,
            is_reviewed=False,
        )
        db.add(transaction)
        imported += 1

    db.add(
        ImportLog(
            filename=file.filename,
            account_id=account_id,
            rows_imported=imported,
            duplicates_skipped=duplicates,
        )
    )
    db.commit()

    return {"rows_imported": imported, "duplicates_skipped": duplicates}
