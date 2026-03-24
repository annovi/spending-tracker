from __future__ import annotations

import csv
import re
from pathlib import Path
from typing import List

from anthropic import Anthropic
from openai import OpenAI
from sqlalchemy.orm import Session

from ..config import settings
from ..models.category import Category
from ..models.category_rule import CategoryRule


def match_category_rules(
    description: str,
    category_names: List[str],
    rules: List[CategoryRule],
    category_name_by_id: dict[int, str],
) -> str | None:
    """In-memory rule match; no DB or AI. `category_name_by_id` maps category id -> name."""
    valid = set(category_names)
    lowered_desc = description.lower()
    for rule in rules:
        try:
            if re.search(rule.pattern, lowered_desc, re.IGNORECASE):
                name = category_name_by_id.get(rule.category_id)
                if name and name in valid:
                    return name
        except re.error:
            if rule.pattern.lower() in lowered_desc:
                name = category_name_by_id.get(rule.category_id)
                if name and name in valid:
                    return name
    return None


def build_categorization_prompt(description: str, category_names: List[str]) -> str:
    return (
        "You are categorizing personal finance transactions. "
        f"Choose exactly one category from this list: {', '.join(category_names)}. "
        f"Transaction description: '{description}'. "
        "Return only the category name."
    )


def suggest_category(description: str, category_names: List[str], db: Session) -> str | None:
    """Suggest a category for a transaction description using rules and AI."""
    rules = db.query(CategoryRule).order_by(CategoryRule.priority.desc()).all()
    category_name_by_id = {c.id: c.name for c in db.query(Category).all()}
    hit = match_category_rules(description, category_names, rules, category_name_by_id)
    if hit:
        return hit

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
        prompt = build_categorization_prompt(description, category_names)
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
        prompt = build_categorization_prompt(description, category_names)
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


def _master_category_csv_path() -> Path:
    return Path(__file__).resolve().parent.parent / "data" / "master_category.csv"


def create_default_rules(db: Session) -> None:
    """Create default category rules from master_category.csv if none exist."""
    if db.query(CategoryRule).count() > 0:
        return

    categories = {cat.name: cat for cat in db.query(Category).all()}
    csv_path = _master_category_csv_path()
    if not csv_path.is_file():
        return

    seen: set[tuple[str, int]] = set()
    with csv_path.open(newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) < 2:
                continue
            raw_label = row[0].strip()
            category_name = row[1].strip()
            if not raw_label or not category_name:
                continue
            cat = categories.get(category_name)
            if not cat:
                continue
            # Substring match on transaction description (case-insensitive)
            pattern = re.escape(raw_label)
            key = (pattern.lower(), cat.id)
            if key in seen:
                continue
            seen.add(key)
            priority = min(len(raw_label) + 10, 250)
            db.add(
                CategoryRule(
                    pattern=pattern,
                    category_id=cat.id,
                    priority=priority,
                )
            )

    db.commit()
