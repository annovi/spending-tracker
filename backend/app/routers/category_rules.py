from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.category_rule import CategoryRule
from ..schemas import CategoryRuleCreate, CategoryRuleResponse, CategoryRuleUpdate

router = APIRouter(prefix="/category-rules", tags=["category-rules"])


@router.get("/", response_model=List[CategoryRuleResponse])
def list_category_rules(
    skip: int = 0,
    limit: int = Query(default=100, le=1000),
    db: Session = Depends(get_db)
):
    """Get all category rules ordered by priority (descending) then by pattern."""
    rules = db.query(CategoryRule).order_by(CategoryRule.priority.desc(), CategoryRule.pattern).offset(skip).limit(limit).all()
    return rules


@router.post("/", response_model=CategoryRuleResponse)
def create_category_rule(rule: CategoryRuleCreate, db: Session = Depends(get_db)):
    """Create a new category rule."""
    db_rule = CategoryRule(**rule.model_dump())
    db.add(db_rule)
    db.commit()
    db.refresh(db_rule)
    return db_rule


@router.put("/{rule_id}", response_model=CategoryRuleResponse)
def update_category_rule(rule_id: int, rule: CategoryRuleUpdate, db: Session = Depends(get_db)):
    """Update a category rule."""
    db_rule = db.query(CategoryRule).filter(CategoryRule.id == rule_id).first()
    if not db_rule:
        raise HTTPException(status_code=404, detail="Category rule not found")
    
    for field, value in rule.model_dump(exclude_unset=True).items():
        setattr(db_rule, field, value)
    
    db.commit()
    db.refresh(db_rule)
    return db_rule


@router.delete("/{rule_id}")
def delete_category_rule(rule_id: int, db: Session = Depends(get_db)):
    """Delete a category rule."""
    db_rule = db.query(CategoryRule).filter(CategoryRule.id == rule_id).first()
    if not db_rule:
        raise HTTPException(status_code=404, detail="Category rule not found")
    
    db.delete(db_rule)
    db.commit()
    return {"ok": True}
