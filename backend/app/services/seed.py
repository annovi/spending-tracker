from sqlalchemy.orm import Session

from ..models import Category
from ..models.enums import CategoryType


DEFAULT_CATEGORIES = [
    ("Groceries", CategoryType.expense, "#16a34a"),
    ("Rent", CategoryType.expense, "#2563eb"),
    ("Shopping", CategoryType.expense, "#9333ea"),
    ("Subscriptions", CategoryType.expense, "#f59e0b"),
    ("Transport", CategoryType.expense, "#0ea5e9"),
    ("Utilities", CategoryType.expense, "#ef4444"),
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
