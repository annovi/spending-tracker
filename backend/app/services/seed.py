from sqlalchemy.orm import Session

from ..models import Category
from ..models.enums import CategoryType


# Master taxonomy (expense + income) — aligned with finance_google_sheet master_categories
DEFAULT_CATEGORIES: list[tuple[str, CategoryType, str]] = [
    ("Housing", CategoryType.expense, "#2563eb"),
    ("Utilities & Bills", CategoryType.expense, "#ef4444"),
    ("Insurance", CategoryType.expense, "#6366f1"),
    ("Food & Groceries", CategoryType.expense, "#16a34a"),
    ("Health & Medical", CategoryType.expense, "#ec4899"),
    ("Transportation", CategoryType.expense, "#0ea5e9"),
    ("Sports & Fitness", CategoryType.expense, "#f97316"),
    ("Shopping & Clothing", CategoryType.expense, "#9333ea"),
    ("Shopping & Electronics", CategoryType.expense, "#8b5cf6"),
    ("Personal Transfers", CategoryType.expense, "#64748b"),
    ("Subscriptions", CategoryType.expense, "#f59e0b"),
    ("Entertainment", CategoryType.expense, "#a855f7"),
    ("Banking & Fees", CategoryType.expense, "#78716c"),
    ("Taxes", CategoryType.expense, "#dc2626"),
    ("Work & Business", CategoryType.expense, "#0891b2"),
    ("Miscellaneous", CategoryType.expense, "#94a3b8"),
    ("Salary", CategoryType.income, "#22c55e"),
    ("Bonus", CategoryType.income, "#10b981"),
]


def seed_default_categories(db: Session) -> None:
    existing = {name for (name,) in db.query(Category.name).all()}
    for name, category_type, color in DEFAULT_CATEGORIES:
        if name in existing:
            continue
        db.add(Category(name=name, type=category_type, color=color))
    db.commit()
