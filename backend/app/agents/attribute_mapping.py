from __future__ import annotations

from typing import Any

from ..services.product_service import parse_user_query


def map_attributes(message: str, session_context: dict[str, Any] | None = None) -> dict[str, Any]:
    parsed = parse_user_query(message, session_context)
    return {
        "category": parsed.get("category"),
        "tags": parsed.get("tags", []),
        "attributes": parsed.get("attributes", []),
        "use_case": parsed.get("use_case"),
        "brand": parsed.get("brand"),
        "budget": parsed.get("max_budget"),
    }
