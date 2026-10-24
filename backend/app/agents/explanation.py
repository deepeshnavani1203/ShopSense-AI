from __future__ import annotations

from typing import Any

from ..services.product_service import generate_explanation


def build_explanation(product: dict[str, Any], constraints: dict[str, Any], score_details: dict[str, Any]) -> str:
    return generate_explanation(product, constraints, score_details)
