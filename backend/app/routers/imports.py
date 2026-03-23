from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Category, ImportLog, Transaction
from ..services.categorizer import suggest_category
from ..services.csv_parser import parse_transactions_csv


router = APIRouter(prefix="/imports", tags=["imports"])


@router.post("/csv")
async def import_csv(
    file: UploadFile = File(...),
    account_id: int | None = Form(default=None),
    db: Session = Depends(get_db),
):
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported")

    file_bytes = await file.read()
    parsed = parse_transactions_csv(file_bytes)

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

        suggested_category_name = suggest_category(item.description, category_names)
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
