from __future__ import annotations

from typing import Any

from ..services.product_service import candidate_filter, list_products


def retrieve_candidates(constraints: dict[str, Any]) -> list[dict[str, Any]]:
    return candidate_filter(list_products(), constraints)
