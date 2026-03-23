from decimal import Decimal

from pydantic import BaseModel


class MonthlySummary(BaseModel):
    month: str
    income: Decimal
    expense: Decimal
    net: Decimal


class CategoryBreakdown(BaseModel):
    category: str
    total: Decimal
