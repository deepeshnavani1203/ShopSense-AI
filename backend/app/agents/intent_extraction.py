from __future__ import annotations

import json
import logging
from typing import Any

from ..config import settings
from ..services.product_service import parse_user_query

logger = logging.getLogger(__name__)

# Lazy Groq client
_groq_client = None


def _get_groq_client():
    global _groq_client
    if _groq_client is None and settings.groq_configured:
        try:
            from groq import Groq
            _groq_client = Groq(api_key=settings.GROQ_API_KEY)
        except Exception as exc:
            logger.warning("Failed to initialise Groq client: %s", exc)
    return _groq_client


def _call_groq_for_intent(message: str, session_context: dict[str, Any] | None) -> dict[str, Any]:
    client = _get_groq_client()
    if client is None:
        raise RuntimeError("Groq not configured")

    ctx_summary = json.dumps(session_context.get("confirmed_constraints", {}) if session_context else {})
    system_prompt = (
        "You are a structured intent extractor for an e-commerce shopping assistant. "
        "Return ONLY valid JSON with no markdown, no prose, and no additional keys."
    )
    user_prompt = (
        f"Extract from this shopping query: \"{message}\".\n"
        f"Prior session context (confirmed constraints): {ctx_summary}.\n"
        "Return JSON with exactly these keys:\n"
        "  intent_type: one of gift|self_use|replacement|comparison\n"
        "  constraints: array of {field, operator, value} for explicit constraints\n"
        "  implicit_constraints: array of strings (e.g. 'low-impact', 'joint-support')\n"
        "  category: string or null (one of: footwear, electronics, outdoor, home-kitchen, fitness, books, fashion, gifts, all)\n"
        "  budget: number or null\n"
        "  brand: string or null\n"
        "  confidence: float 0.0-1.0\n"
        "No markdown, no prose — raw JSON only."
    )

    response = client.chat.completions.create(
        model=settings.GROQ_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.1,
        max_tokens=400,
        response_format={"type": "json_object"},
    )
    return json.loads(response.choices[0].message.content)


def extract_intent(message: str, session_context: dict[str, Any] | None = None) -> dict[str, Any]:
    """Extract intent using Groq LLM; fall back to parse_user_query on error."""
    explicit_constraints: list[dict[str, Any]] = []
    implicit_constraints: list[str] = []
    intent_type = "self_use"
    category = None
    budget = None
    brand = None
    confidence = 0.82

    try:
        groq_result = _call_groq_for_intent(message, session_context)
        intent_type = groq_result.get("intent_type", "self_use")
        explicit_constraints = groq_result.get("constraints", []) or []
        implicit_constraints = groq_result.get("implicit_constraints", []) or []
        category = groq_result.get("category")
        budget = groq_result.get("budget")
        brand = groq_result.get("brand")
        confidence = float(groq_result.get("confidence", 0.82))
    except Exception as exc:
        logger.warning("Groq intent extraction failed (%s); using parse_user_query fallback.", exc)
        payload = parse_user_query(message, session_context)
        intent_type = payload.get("intent", "self_use")
        category = payload.get("category")
        budget = payload.get("max_budget")
        brand = payload.get("brand")
        confidence = 0.82

    # Derive budget from explicit_constraints if not set by Groq directly
    max_budget = budget
    min_budget = None
    for c in explicit_constraints:
        field = c.get("field", "")
        operator = c.get("operator", "")
        value = c.get("value")
        if field == "price" and value is not None:
            try:
                v = float(value)
            except (TypeError, ValueError):
                continue
            if operator in ("<=", "<", "lte"):
                max_budget = v
            elif operator in (">=", ">", "gte"):
                min_budget = v
            elif operator in ("=", "=="):
                max_budget = v

    # Carry forward fallback tags
    fallback_payload = parse_user_query(message, session_context)
    tags = fallback_payload.get("tags", [])
    attributes = fallback_payload.get("attributes", [])
    # Merge implicit_constraints into tags
    for ic in implicit_constraints:
        slug = ic.lower().replace(" ", "-")
        if slug not in tags:
            tags.append(slug)

    return {
        "purchase_intent": intent_type,
        "category": category,
        "budget": budget,
        "max_budget": max_budget,
        "min_budget": min_budget,
        "brand": brand,
        "tags": tags,
        "attributes": attributes,
        "confidence": confidence,
        "constraints": explicit_constraints,
        "implicit_constraints": implicit_constraints,
        "intent_type": intent_type,
    }
