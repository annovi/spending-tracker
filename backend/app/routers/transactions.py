from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Category, Transaction
from ..schemas.transaction import (
    BulkRecategorizeRequest,
    RecategorizationSuggestion,
    TransactionCreate,
    TransactionOut,
    TransactionUpdate,
)
from ..services.categorizer import suggest_category


router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.get("", response_model=list[TransactionOut])
def list_transactions(
    skip: int = 0,
    limit: int = Query(default=100, le=1000),
    category_id: int | None = None,
    account_id: int | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    db: Session = Depends(get_db),
):
    query = db.query(Transaction)
    if category_id:
        query = query.filter(Transaction.category_id == category_id)
    if account_id:
        query = query.filter(Transaction.account_id == account_id)
    if date_from is not None:
        query = query.filter(Transaction.date >= date_from)
    if date_to is not None:
        query = query.filter(Transaction.date <= date_to)

    return query.order_by(Transaction.date.desc(), Transaction.id.desc()).offset(skip).limit(limit).all()


@router.post("", response_model=TransactionOut)
def create_transaction(payload: TransactionCreate, db: Session = Depends(get_db)):
    transaction = Transaction(**payload.model_dump())
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction


@router.get("/review/suggestions", response_model=list[RecategorizationSuggestion])
def recategorization_suggestions(
    limit: int = Query(default=200, le=1000),
    date_from: date | None = None,
    date_to: date | None = None,
    recompute: bool = Query(
        default=False,
        description="If true, ignore cached suggestions and re-run rules/AI (slower).",
    ),
    db: Session = Depends(get_db),
):
    categories = db.query(Category).order_by(Category.name.asc()).all()
    category_names = [category.name for category in categories]
    category_id_by_name = {category.name: category.id for category in categories}
    category_name_by_id = {category.id: category.name for category in categories}

    q = db.query(Transaction)
    if date_from is not None:
        q = q.filter(Transaction.date >= date_from)
    if date_to is not None:
        q = q.filter(Transaction.date <= date_to)
    transactions = q.order_by(Transaction.date.desc(), Transaction.id.desc()).limit(limit).all()

    suggestions: list[RecategorizationSuggestion] = []
    dirty = False
    for transaction in transactions:
        if transaction.is_reviewed:
            continue

        predicted_id: int | None = None
        if not recompute and transaction.cached_suggested_category_id is not None:
            cid = transaction.cached_suggested_category_id
            if cid in category_name_by_id:
                predicted_id = cid

        if predicted_id is None:
            predicted_name = suggest_category(transaction.description, category_names, db)
            new_id = category_id_by_name.get(predicted_name) if predicted_name else None
            if transaction.cached_suggested_category_id != new_id:
                transaction.cached_suggested_category_id = new_id
                dirty = True
            predicted_id = new_id

        if not predicted_id:
            continue

        predicted_name = category_name_by_id.get(predicted_id)
        if not predicted_name:
            continue

        current_name = category_name_by_id.get(transaction.category_id) if transaction.category_id else None
        if transaction.category_id == predicted_id:
            continue

        suggestions.append(
            RecategorizationSuggestion(
                transaction_id=transaction.id,
                date=transaction.date,
                description=transaction.display_name or transaction.description,
                amount=transaction.amount,
                current_category_id=transaction.category_id,
                current_category_name=current_name,
                suggested_category_id=predicted_id,
                suggested_category_name=predicted_name,
            )
        )

    if dirty:
        db.commit()

    return suggestions


@router.post("/review/apply")
def apply_bulk_recategorization(payload: BulkRecategorizeRequest, db: Session = Depends(get_db)):
    updated = 0
    for item in payload.items:
        transaction = db.query(Transaction).filter(Transaction.id == item.transaction_id).first()
        if not transaction:
            continue
        transaction.category_id = item.category_id
        transaction.is_reviewed = True
        transaction.cached_suggested_category_id = None
        updated += 1

    db.commit()
    return {"updated": updated}


@router.get("/{transaction_id}", response_model=TransactionOut)
def get_transaction(transaction_id: int, db: Session = Depends(get_db)):
    transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction


@router.patch("/{transaction_id}", response_model=TransactionOut)
def update_transaction(transaction_id: int, payload: TransactionUpdate, db: Session = Depends(get_db)):
    transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    updates = payload.model_dump(exclude_unset=True)
    invalidate = {"description", "display_name", "category_id", "is_reviewed"} & updates.keys()
    if invalidate:
        transaction.cached_suggested_category_id = None
    for key, value in updates.items():
        setattr(transaction, key, value)

    db.commit()
    db.refresh(transaction)
    return transaction


@router.delete("/{transaction_id}")
def delete_transaction(transaction_id: int, db: Session = Depends(get_db)):
    transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    db.delete(transaction)
    db.commit()
    return {"ok": True}
