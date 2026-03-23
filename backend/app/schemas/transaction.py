from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel


class TransactionBase(BaseModel):
    date: date
    description: str
    display_name: str | None = None
    amount: Decimal
    category_id: int | None = None
    account_id: int | None = None
    notes: str | None = None
    is_reviewed: bool = False
    source: str = "manual"


class TransactionCreate(TransactionBase):
    import_hash: str | None = None


class TransactionUpdate(BaseModel):
    date: date | None = None
    description: str | None = None
    display_name: str | None = None
    amount: Decimal | None = None
    category_id: int | None = None
    account_id: int | None = None
    notes: str | None = None
    is_reviewed: bool | None = None


class TransactionOut(TransactionBase):
    id: int
    import_hash: str | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class RecategorizationSuggestion(BaseModel):
    transaction_id: int
    date: date
    description: str
    amount: Decimal
    current_category_id: int | None = None
    current_category_name: str | None = None
    suggested_category_id: int
    suggested_category_name: str


class BulkRecategorizeItem(BaseModel):
    transaction_id: int
    category_id: int


class BulkRecategorizeRequest(BaseModel):
    items: list[BulkRecategorizeItem]
