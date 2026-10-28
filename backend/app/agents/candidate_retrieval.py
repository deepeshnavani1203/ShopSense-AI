from __future__ import annotations

import logging
from typing import Any

from ..database import db_find_all
from ..services.product_service import candidate_filter, list_products

logger = logging.getLogger(__name__)


async def retrieve_candidates(constraints: dict[str, Any]) -> list[dict[str, Any]]:
    """Query MongoDB products collection; fall back to file-based list_products."""
    category = constraints.get("category")
    max_budget = constraints.get("max_budget")
    tags = constraints.get("tags", [])

    # Build MongoDB query
    mongo_query: dict[str, Any] = {}
    if category and category != "all":
        mongo_query["category"] = category
    if max_budget:
        mongo_query["price"] = {"$lte": float(max_budget)}
    if tags:
        mongo_query["tags"] = {"$in": tags}

    raw = await db_find_all("products", mongo_query)

    if not raw:
        logger.info("MongoDB returned no products; using file-based fallback.")
        raw = list_products()

    # Strip _id in case any slipped through
    for doc in raw:
        doc.pop("_id", None)

    # Apply residual in-process filtering (handles tag intersection and edge cases)
    return candidate_filter(raw, constraints)
