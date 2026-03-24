"""Shared CSV / sheet import pipeline into Transaction rows."""

from __future__ import annotations

from sqlalchemy.orm import Session

from ..models import Account, Category, ImportLog, Transaction
from ..models.enums import AccountType
from .categorizer import suggest_category
from .csv_parser_v2 import ParsedTransaction

_CREDIT_CARD_KEYWORDS = {"visa", "amex", "mastercard", "mc", "credit card", "credit"}


def _guess_account_type(name: str) -> AccountType:
    lower = name.lower()
    for kw in _CREDIT_CARD_KEYWORDS:
        if kw in lower:
            return AccountType.credit_card
    return AccountType.bank


def _resolve_account_id(
    db: Session,
    name: str,
    cache: dict[str, int],
) -> int:
    """Look up an account by name (case-insensitive), create it if missing."""
    key = name.strip().lower()
    if key in cache:
        return cache[key]
    account = db.query(Account).filter(Account.name.ilike(key)).first()
    if not account:
        account = Account(name=name.strip(), type=_guess_account_type(name))
        db.add(account)
        db.flush()
    cache[key] = account.id
    return account.id


def import_parsed_transactions(
    db: Session,
    parsed: list[ParsedTransaction],
    filename: str,
    account_id: int | None = None,
) -> dict[str, int]:
    categories = db.query(Category).all()
    category_names = [c.name for c in categories]
    category_map = {c.name: c.id for c in categories}

    account_cache: dict[str, int] = {}

    imported = 0
    duplicates = 0

    for item in parsed:
        existing = (
            db.query(Transaction).filter(Transaction.import_hash == item.import_hash).first()
        )
        if existing:
            duplicates += 1
            continue

        suggested_category_name = suggest_category(item.description, category_names, db)
        suggested_category_id = (
            category_map.get(suggested_category_name) if suggested_category_name else None
        )

        row_account_id = account_id
        if row_account_id is None and item.account_name:
            row_account_id = _resolve_account_id(db, item.account_name, account_cache)

        db.add(
            Transaction(
                date=item.date,
                description=item.description,
                amount=item.amount,
                account_id=row_account_id,
                category_id=suggested_category_id,
                source=item.source,
                import_hash=item.import_hash,
                is_reviewed=False,
            )
        )
        imported += 1

    db.add(
        ImportLog(
            filename=filename,
            account_id=account_id,
            rows_imported=imported,
            duplicates_skipped=duplicates,
        )
    )
    db.commit()

    return {"rows_imported": imported, "duplicates_skipped": duplicates}
