from decimal import Decimal

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Category, Transaction


router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/summary")
def monthly_summary(db: Session = Depends(get_db)):
    monthly = (
        db.query(
            func.to_char(Transaction.date, "YYYY-MM").label("month"),
            func.sum(Transaction.amount).label("net"),
        )
        .group_by(func.to_char(Transaction.date, "YYYY-MM"))
        .order_by(func.to_char(Transaction.date, "YYYY-MM").asc())
        .all()
    )

    result = []
    for row in monthly:
        result.append(
            {
                "month": row.month,
                "net": row.net,
                "income": row.net if row.net > 0 else Decimal("0"),
                "expense": abs(row.net) if row.net < 0 else Decimal("0"),
            }
        )

    return result


@router.get("/categories")
def category_breakdown(db: Session = Depends(get_db)):
    rows = (
        db.query(Category.name, func.sum(Transaction.amount).label("total"))
        .join(Transaction, Transaction.category_id == Category.id)
        .group_by(Category.name)
        .order_by(func.sum(Transaction.amount).asc())
        .all()
    )

    return [{"category": row.name, "total": row.total} for row in rows]
