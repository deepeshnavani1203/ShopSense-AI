from __future__ import annotations

from typing import Any

from ..services.product_service import build_recommendation_response


def build_fallback(message: str, constraints: dict[str, Any]) -> dict[str, Any]:
    response = build_recommendation_response(message, constraints)
    return {
        "original_constraints": constraints,
        "relaxed_constraints": [],
        "recommendations": response.get("recommendations", []),
        "alternatives": response.get("alternatives", []),
    }
