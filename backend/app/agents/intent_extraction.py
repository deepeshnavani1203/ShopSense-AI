from __future__ import annotations

from typing import Any

from ..services.product_service import parse_user_query


def extract_intent(message: str, session_context: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = parse_user_query(message, session_context)
    return {
        "purchase_intent": payload.get("intent", "self_use"),
        "category": payload.get("category"),
        "budget": payload.get("budget"),
        "max_budget": payload.get("max_budget"),
        "min_budget": payload.get("min_budget"),
        "brand": payload.get("brand"),
        "tags": payload.get("tags", []),
        "attributes": payload.get("attributes", []),
        "confidence": 0.82,
    }
