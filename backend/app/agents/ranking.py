from __future__ import annotations

from typing import Any

from ..services.product_service import rank_products


def rank_candidates(products: list[dict[str, Any]], constraints: dict[str, Any]) -> list[dict[str, Any]]:
    return rank_products(products, constraints)
