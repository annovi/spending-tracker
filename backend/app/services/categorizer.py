from __future__ import annotations

from openai import OpenAI

from ..config import settings


DEFAULT_KEYWORDS = {
    "salary": "Salary",
    "payroll": "Salary",
    "amazon": "Shopping",
    "whole foods": "Groceries",
    "trader joe": "Groceries",
    "netflix": "Subscriptions",
    "spotify": "Subscriptions",
    "uber": "Transport",
    "lyft": "Transport",
    "rent": "Rent",
}


def suggest_category(description: str, category_names: list[str]) -> str | None:
    lowered = description.lower()
    for keyword, category in DEFAULT_KEYWORDS.items():
        if keyword in lowered and category in category_names:
            return category

    if not settings.openai_api_key:
        return None

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
