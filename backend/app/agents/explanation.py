from __future__ import annotations

import json
import logging
from typing import Any

from ..config import settings
from ..services.product_service import generate_explanation

logger = logging.getLogger(__name__)

_groq_client = None


def _get_groq_client():
    global _groq_client
    if _groq_client is None and settings.groq_configured:
        try:
            from groq import Groq
            _groq_client = Groq(api_key=settings.GROQ_API_KEY)
        except Exception as exc:
            logger.warning("Failed to initialise Groq client in explanation: %s", exc)
    return _groq_client


def _call_groq_for_explanation(
    product: dict[str, Any],
    constraints: dict[str, Any],
    score_details: dict[str, Any],
) -> str:
    client = _get_groq_client()
    if client is None:
        raise RuntimeError("Groq not configured")

    unmet = product.get("unmet_constraints", [])
    system_prompt = (
        "You are a friendly shopping assistant explaining why a product is recommended."
    )
    user_prompt = (
        f"Product: {product.get('name')} "
        f"({product.get('category')}, ₹{product.get('price')}).\n"
        f"Shopper constraints: {json.dumps(constraints)}.\n"
        f"Fit scores (0–100): {json.dumps(score_details)}.\n"
        f"Unmet constraints: {json.dumps(unmet)}.\n\n"
        "Write exactly 2 sentences:\n"
        "Sentence 1: Explain specifically why this product matches the stated request "
        "(reference the actual constraint names or product features, not generic praise).\n"
        "Sentence 2: If there are unmet constraints, flag them clearly. "
        "Otherwise write 'Fully meets all stated requirements.'\n"
        "No bullet points, no markdown, no greeting."
    )
    response = client.chat.completions.create(
        model=settings.GROQ_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.3,
        max_tokens=150,
    )
    return response.choices[0].message.content.strip()


def build_explanation(
    product: dict[str, Any],
    constraints: dict[str, Any],
    score_details: dict[str, Any],
) -> str:
    """Generate plain-language explanation via Groq; fall back to rule-based."""
    try:
        return _call_groq_for_explanation(product, constraints, score_details)
    except Exception as exc:
        logger.warning("Groq explanation failed (%s); using generate_explanation fallback.", exc)
        return generate_explanation(product, constraints, score_details)
