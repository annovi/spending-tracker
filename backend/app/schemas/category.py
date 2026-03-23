from __future__ import annotations

from pydantic import BaseModel

from ..models.enums import CategoryType


class CategoryBase(BaseModel):
    name: str
    type: CategoryType
    color: str = "#64748b"
    icon: str | None = None


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: str | None = None
    type: CategoryType | None = None
    color: str | None = None
    icon: str | None = None


class CategoryOut(CategoryBase):
    id: int

    class Config:
        from_attributes = True
