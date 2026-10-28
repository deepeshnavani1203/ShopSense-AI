from __future__ import annotations

import json
import logging
from typing import Any

from ..config import settings
from ..services.product_service import score_product

logger = logging.getLogger(__name__)

_groq_client = None


def _get_groq_client():
    global _groq_client
    if _groq_client is None and settings.groq_configured:
        try:
            from groq import Groq
            _groq_client = Groq(api_key=settings.GROQ_API_KEY)
        except Exception as exc:
            logger.warning("Failed to initialise Groq client in best_pick: %s", exc)
    return _groq_client


def pick_best(
    products: list[dict[str, Any]],
    constraints: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Given a list of products (from compare selection), decide which is the single best pick.
    Uses Groq LLM when available; falls back to highest fit_score.
    Returns: {product_id, name, reason, confidence}
    """
    if not products:
        return {}

    # Fallback: highest fit_score wins
    def _fallback_pick() -> dict[str, Any]:
        scored = []
        for p in products:
            fit = p.get("fit_score")
            if fit is None:
                metrics = score_product(p, constraints or {})
                fit = metrics["fit_score"] / 100
            scored.append((float(fit), p))
        scored.sort(key=lambda x: x[0], reverse=True)
        best_score, best = scored[0]
        return {
            "product_id": best.get("product_id"),
            "name": best.get("name"),
            "reason": (
                f"Highest overall fit score ({best_score:.0%}) among compared products. "
                f"Best value at ₹{best.get('price', 0):,} in the {best.get('category', '')} category."
            ),
            "confidence": round(best_score, 2),
        }

    client = _get_groq_client()
    if client is None:
        return _fallback_pick()

    try:
        product_summaries = []
        for p in products:
            fit = p.get("fit_score")
            if fit is None:
                metrics = score_product(p, constraints or {})
                fit = round(metrics["fit_score"] / 100, 2)
            product_summaries.append({
                "product_id": p.get("product_id"),
                "name": p.get("name"),
                "category": p.get("category"),
                "price": p.get("price"),
                "tags": p.get("tags", []),
                "fit_score": fit,
                "rating": p.get("rating"),
                "description": p.get("description", "")[:120],
            })

        system_prompt = (
            "You are a shopping advisor picking the single best product from a comparison list. "
            "Return ONLY valid JSON."
        )
        user_prompt = (
            f"Products to compare: {json.dumps(product_summaries)}\n"
            f"Shopper constraints: {json.dumps(constraints or {})}\n"
            "Pick the ONE best product. Consider fit_score, price-value, category relevance, and rating.\n"
            'Return JSON: {"product_id": str, "name": str, "reason": str (2 sentences), "confidence": float 0-1}'
        )
        response = client.chat.completions.create(
            model=settings.GROQ_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.2,
            max_tokens=200,
            response_format={"type": "json_object"},
        )
        data = json.loads(response.choices[0].message.content)
        return {
            "product_id": data.get("product_id"),
            "name": data.get("name"),
            "reason": data.get("reason", "Best overall match across all criteria."),
            "confidence": float(data.get("confidence", 0.8)),
        }
    except Exception as exc:
        logger.warning("Groq best_pick failed (%s); using fallback.", exc)
        return _fallback_pick()
