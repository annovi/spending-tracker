from datetime import date
from decimal import Decimal

from fastapi import APIRouter, Depends, Query
from sqlalchemy import String, func
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Category, Transaction
from ..schemas.analytics import CategoryBreakdown, MonthlySummary


router = APIRouter(prefix="/analytics", tags=["analytics"])


def _month_key_expr():
    """YYYY-MM grouping; works on PostgreSQL and SQLite (tests)."""
    return func.substr(func.cast(Transaction.date, String), 1, 7)


def _apply_date_range(query, date_from: date | None, date_to: date | None):
    if date_from is not None:
        query = query.filter(Transaction.date >= date_from)
    if date_to is not None:
        query = query.filter(Transaction.date <= date_to)
    return query


@router.get("/summary", response_model=list[MonthlySummary])
def monthly_summary(
    db: Session = Depends(get_db),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
):
    month_key = _month_key_expr().label("month")
    q = db.query(
        month_key,
        func.sum(Transaction.amount).label("net"),
    )
    q = _apply_date_range(q, date_from, date_to)
    monthly = q.group_by(month_key).order_by(month_key.asc()).all()

    result = []
    for row in monthly:
        result.append(
            MonthlySummary(
                month=row.month,
                net=row.net,
                income=row.net if row.net > 0 else Decimal("0"),
                expense=abs(row.net) if row.net < 0 else Decimal("0"),
            )
        )

    return result


@router.get("/categories", response_model=list[CategoryBreakdown])
def category_breakdown(
    db: Session = Depends(get_db),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
):
    q = (
        db.query(Category.name, func.sum(Transaction.amount).label("total"))
        .join(Transaction, Transaction.category_id == Category.id)
    )
    q = _apply_date_range(q, date_from, date_to)
    rows = q.group_by(Category.name).order_by(func.sum(Transaction.amount).asc()).all()

    return [CategoryBreakdown(category=row.name, total=row.total) for row in rows]
