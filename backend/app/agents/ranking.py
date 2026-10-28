from __future__ import annotations

from typing import Any

from ..services.product_service import score_product


def rank_candidates(
    products: list[dict[str, Any]],
    constraints: dict[str, Any],
) -> list[dict[str, Any]]:
    """
    Score and rank products against the full constraint set.

    Weighting:
      - Explicit constraints outweigh implicit ones.
      - Partial-match penalty: −10 per unmet explicit constraint (capped).
      - Implicit tag bonus: +3 per matching tag (capped at +12).
      - fit_score returned as float in [0, 1].
    """
    explicit_constraints: list[dict[str, Any]] = constraints.get("explicit_constraints", [])
    implicit_tags: list[str] = constraints.get("implicit_constraints", [])
    # Also consider tags as implicit signals
    constraint_tags: list[str] = constraints.get("tags", [])

    ranked: list[dict[str, Any]] = []

    for product in products:
        metrics = score_product(product, constraints)

        category_match: float = metrics["category_match"]   # 0–100
        use_case_fit: float = metrics["use_case_fit"]       # 0–100
        feature_match: float = metrics["feature_match"]     # 0–100
        budget_fit: float = metrics["budget_fit"]           # 0–100
        rating_signal: float = metrics["rating_signal"]     # 0–100
        unmet: list[str] = metrics.get("unmet_constraints", [])

        # Weighted base score (0–100)
        base = (
            category_match * 0.25
            + use_case_fit * 0.25
            + feature_match * 0.20
            + budget_fit * 0.15
            + rating_signal * 0.15
        )

        # Explicit constraint penalty
        penalty = min(len(unmet) * 10, 30)

        # Implicit tag bonus
        product_tags = set(product.get("tags", []))
        product_use_cases = set(product.get("use_cases", []))
        all_product_terms = product_tags | product_use_cases

        bonus = 0
        for tag in implicit_tags + constraint_tags:
            slug = tag.lower().replace(" ", "-")
            if slug in all_product_terms or tag.lower() in all_product_terms:
                bonus += 3
        bonus = min(bonus, 12)

        raw_score = max(0.0, min(100.0, base - penalty + bonus))
        fit_score = round(raw_score / 100.0, 4)

        ranked.append({
            **product,
            "fit_score": fit_score,
            "score_breakdown": {
                "category_match": category_match,
                "use_case_fit": use_case_fit,
                "feature_match": feature_match,
                "budget_fit": budget_fit,
                "rating_signal": rating_signal,
            },
            "unmet_constraints": unmet,
        })

    ranked.sort(key=lambda item: item["fit_score"], reverse=True)
    return ranked
