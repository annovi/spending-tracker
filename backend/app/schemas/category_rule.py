from __future__ import annotations

from pydantic import BaseModel, Field


class CategoryRuleBase(BaseModel):
    pattern: str = Field(..., min_length=1, max_length=200, description="Pattern to match in transaction description")
    category_id: int = Field(..., description="Category ID to apply when pattern matches")
    priority: int = Field(default=0, description="Priority of rule (higher values checked first)")


class CategoryRuleCreate(CategoryRuleBase):
    pass


class CategoryRuleUpdate(BaseModel):
    pattern: str | None = Field(None, min_length=1, max_length=200)
    category_id: int | None = None
    priority: int | None = None


class CategoryRuleResponse(CategoryRuleBase):
    id: int
    
    class Config:
        from_attributes = True
