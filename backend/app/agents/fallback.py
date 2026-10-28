from __future__ import annotations

import copy
import logging
from typing import Any

from ..services.product_service import candidate_filter, list_products, rank_products

logger = logging.getLogger(__name__)

# Relax in this order: budget first, then tags, then category
_RELAXATION_ORDER = ["max_budget", "tags", "category"]

# Minimum fit_score threshold for "good enough" results
_MIN_FIT_THRESHOLD = 0.40


def build_fallback(
    message: str,
    constraints: dict[str, Any],
    ranked_products: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """
    Detect low-confidence / empty result sets and propose relaxed alternatives.
    Returns a dict with fallback_triggered, relaxed_constraint, alternatives, etc.
    """
    # If we already have strong results, no fallback needed
    if ranked_products:
        best_score = ranked_products[0].get("fit_score", 0.0)
        if isinstance(best_score, (int, float)) and float(best_score) >= _MIN_FIT_THRESHOLD:
            return {
                "fallback_triggered": False,
                "relaxed_constraint": None,
                "alternatives": [],
                "trade_off_explanation": None,
                "original_constraints": constraints,
                "relaxed_constraints": constraints,
            }

    all_products = list_products()
    original_constraints = copy.deepcopy(constraints)

    for field in _RELAXATION_ORDER:
        relaxed = copy.deepcopy(constraints)
        label: str | None = None

        if field == "max_budget":
            budget = constraints.get("max_budget")
            if not budget:
                continue
            new_max = float(budget) * 1.30
            relaxed["max_budget"] = new_max
            label = f"budget relaxed by 30% to ₹{new_max:.0f}"

        elif field == "tags":
            tags = constraints.get("tags", [])
            if not tags:
                continue
            dropped = tags[-1]
            relaxed["tags"] = tags[:-1]
            label = f"removed '{dropped}' filter"

        elif field == "category":
            if constraints.get("category") in (None, "all"):
                continue
            relaxed["category"] = "all"
            label = "expanded to all categories"

        else:
            continue

        candidates = candidate_filter(all_products, relaxed)
        if not candidates:
            continue

        ranked = rank_products(candidates, relaxed)
        top3 = ranked[:3]
        if top3:
            alternatives = [
                {
                    "product_id": p.get("product_id"),
                    "name": p.get("name"),
                    "brand": p.get("brand"),
                    "category": p.get("category"),
                    "price": p.get("price"),
                    "currency": p.get("currency", "INR"),
                    "image": p.get("image"),
                    "fit_score": p.get("fit_score"),
                    "explanation": p.get("explanation", ""),
                    "reasons": [],
                    "unmet_constraints": p.get("unmet_constraints", []),
                    "stock_status": p.get("stock_status", "in_stock"),
                    "match_summary": p.get("score_breakdown", {}),
                }
                for p in top3
            ]
            return {
                "fallback_triggered": True,
                "relaxed_constraint": label,
                "alternatives": alternatives,
                "trade_off_explanation": f"No exact match found. {label}.",
                "original_constraints": original_constraints,
                "relaxed_constraints": relaxed,
            }

    # Nothing found even after relaxation
    return {
        "fallback_triggered": True,
        "relaxed_constraint": None,
        "alternatives": [],
        "trade_off_explanation": "No matching products found even after relaxing constraints.",
        "original_constraints": original_constraints,
        "relaxed_constraints": constraints,
    }
