from __future__ import annotations

import re
from typing import List

from anthropic import Anthropic
from openai import OpenAI
from sqlalchemy.orm import Session

from ..config import settings
from ..models.category import Category
from ..models.category_rule import CategoryRule


def suggest_category(description: str, category_names: List[str], db: Session) -> str | None:
    """Suggest a category for a transaction description using rules and AI."""
    
    # First, try to match against database rules
    rules = db.query(CategoryRule).order_by(CategoryRule.priority.desc()).all()
    lowered_desc = description.lower()
    
    for rule in rules:
        # Support both exact string match and regex
        try:
            # Try regex first
            if re.search(rule.pattern, lowered_desc, re.IGNORECASE):
                category = db.query(Category).filter(Category.id == rule.category_id).first()
                if category and category.name in category_names:
                    return category.name
        except re.error:
            # If regex is invalid, fall back to simple string match
            if rule.pattern.lower() in lowered_desc:
                category = db.query(Category).filter(Category.id == rule.category_id).first()
                if category and category.name in category_names:
                    return category.name
    
    # If no rule matches and AI is configured, try AI categorization
    if settings.ai_provider == "openai" and settings.openai_api_key:
        return _categorize_with_openai(description, category_names)
    elif settings.ai_provider == "claude" and settings.claude_api_key:
        return _categorize_with_claude(description, category_names)
    
    return None


def _categorize_with_openai(description: str, category_names: List[str]) -> str | None:
    """Categorize using OpenAI API."""
    try:
        client = OpenAI(api_key=settings.openai_api_key)
        prompt = (
            "You are categorizing personal finance transactions. "
            f"Choose exactly one category from this list: {', '.join(category_names)}. "
            f"Transaction description: '{description}'. "
            "Return only the category name."
        )
        completion = client.chat.completions.create(
            model=settings.openai_model,
            messages=[
                {"role": "system", "content": "Return only one category name from the provided list."},
                {"role": "user", "content": prompt},
            ],
            temperature=0,
        )
        content = (completion.choices[0].message.content or "").strip()
        return content if content in category_names else None
    except Exception:
        return None


def _categorize_with_claude(description: str, category_names: List[str]) -> str | None:
    """Categorize using Claude API."""
    try:
        client = Anthropic(api_key=settings.claude_api_key)
        prompt = (
            "You are categorizing personal finance transactions. "
            f"Choose exactly one category from this list: {', '.join(category_names)}. "
            f"Transaction description: '{description}'. "
            "Return only the category name."
        )
        message = client.messages.create(
            model=settings.claude_model,
            max_tokens=100,
            temperature=0,
            system="Return only one category name from the provided list.",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        content = (message.content[0].text if message.content else "").strip()
        return content if content in category_names else None
    except Exception:
        return None


def create_default_rules(db: Session) -> None:
    """Create default category rules if none exist."""
    if db.query(CategoryRule).count() > 0:
        return
    
    # Get default categories
    categories = {cat.name: cat for cat in db.query(Category).all()}
    
    default_rules = [
        # Income rules
        (r"salary|payroll|paycheck", "Salary", 10),
        (r"deposit|direct deposit", "Salary", 5),
        
        # Shopping rules
        (r"amazon|amzn", "Shopping", 10),
        (r"walmart|target", "Shopping", 10),
        (r"costco|sam's club", "Shopping", 10),
        (r"etsy|ebay", "Shopping", 10),
        
        # Groceries rules
        (r"whole foods|wholefoods", "Groceries", 10),
        (r"trader joe|traderjoe", "Groceries", 10),
        (r"safeway|kroger|albertsons", "Groceries", 10),
        (r"publix|food lion", "Groceries", 10),
        
        # Subscription rules
        (r"netflix", "Subscriptions", 10),
        (r"spotify", "Subscriptions", 10),
        (r"apple\.com\b.*subscription", "Subscriptions", 10),
        (r"disney\+", "Subscriptions", 10),
        (r"hulu", "Subscriptions", 10),
        (r"youtube premium", "Subscriptions", 10),
        
        # Transport rules
        (r"uber|lyft", "Transport", 10),
        (r"gas station|chevron|shell|exxon", "Transport", 10),
        (r"parking", "Transport", 10),
        (r"metro|subway|bus", "Transport", 10),
        
        # Rent/Utilities
        (r"rent|lease", "Rent", 10),
        (r"electric|electricity|utility", "Utilities", 10),
        (r"water|sewer", "Utilities", 10),
        (r"gas bill|natural gas", "Utilities", 10),
        (r"internet|wifi|broadband", "Utilities", 10),
        
        # Dining rules
        (r"starbucks", "Dining", 10),
        (r"mcdonald|burger king|wendy", "Dining", 10),
        (r"restaurant|dinner|lunch", "Dining", 5),
        (r"doordash|uber eats|grubhub", "Dining", 10),
        
        # Healthcare rules
        (r"pharmacy|cv|walgreens", "Healthcare", 10),
        (r"doctor|medical|clinic", "Healthcare", 10),
        (r"dental|dentist", "Healthcare", 10),
        
        # Entertainment rules
        (r"movie|cinema|theater", "Entertainment", 10),
        (r"concert|show", "Entertainment", 10),
        (r"game|steam|playstation", "Entertainment", 10),
    ]
    
    for pattern, category_name, priority in default_rules:
        if category_name in categories:
            rule = CategoryRule(
                pattern=pattern,
                category_id=categories[category_name].id,
                priority=priority
            )
            db.add(rule)
    
    db.commit()
