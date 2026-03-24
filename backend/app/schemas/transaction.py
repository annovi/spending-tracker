from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel


class TransactionBase(BaseModel):
    date: date
    description: str
    display_name: Optional[str] = None
    amount: Decimal
    category_id: Optional[int] = None
    account_id: Optional[int] = None
    notes: Optional[str] = None
    is_reviewed: bool = False
    source: str = "manual"


class TransactionCreate(TransactionBase):
    import_hash: Optional[str] = None


class TransactionUpdate(BaseModel):
    date: Optional[date] = None
    description: Optional[str] = None
    display_name: Optional[str] = None
    amount: Optional[Decimal] = None
    category_id: Optional[int] = None
    account_id: Optional[int] = None
    notes: Optional[str] = None
    is_reviewed: Optional[bool] = None


class TransactionOut(TransactionBase):
    id: int
    import_hash: Optional[str] = None
    cached_suggested_category_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class RecategorizationSuggestion(BaseModel):
    transaction_id: int
    date: date
    description: str
    amount: Decimal
    current_category_id: Optional[int] = None
    current_category_name: Optional[str] = None
    suggested_category_id: int
    suggested_category_name: str


class BulkRecategorizeItem(BaseModel):
    transaction_id: int
    category_id: int


class BulkRecategorizeRequest(BaseModel):
    items: List[BulkRecategorizeItem]
