from __future__ import annotations

import json
import logging
from typing import Any

from ..config import settings
from ..services.product_service import parse_user_query

logger = logging.getLogger(__name__)

_groq_client = None

_VALID_CATEGORIES = {
    "footwear", "electronics", "outdoor", "home-kitchen",
    "fitness", "books", "fashion", "gifts", "all",
}

_VALID_TAGS = {
    "lightweight", "comfortable", "budget", "durable", "waterproof",
    "wireless", "student", "hiking", "travel", "gaming", "office",
    "giftable", "fitness", "running", "casual", "premium",
    "low-impact", "joint-support",
}


def _get_groq_client():
    global _groq_client
    if _groq_client is None and settings.groq_configured:
        try:
            from groq import Groq
            _groq_client = Groq(api_key=settings.GROQ_API_KEY)
        except Exception as exc:
            logger.warning("Failed to initialise Groq client in attribute_mapping: %s", exc)
    return _groq_client


def _call_groq_for_mapping(
    message: str,
    intent: dict[str, Any] | None,
    session_context: dict[str, Any] | None,
) -> dict[str, Any]:
    client = _get_groq_client()
    if client is None:
        raise RuntimeError("Groq not configured")

    system_prompt = (
        "You are a catalog taxonomy mapper for an e-commerce assistant. "
        "Return ONLY valid JSON with no markdown."
    )
    user_prompt = (
        f"Message: \"{message}\".\n"
        f"Extracted intent: {json.dumps(intent or {})}.\n"
        "Map to catalog attributes using ONLY these values:\n"
        f"  category: one of {sorted(_VALID_CATEGORIES)}\n"
        f"  tags: subset of {sorted(_VALID_TAGS)}\n"
        "  use_case: string or null\n"
        'Return JSON: {"category": str, "tags": [str], "use_case": str or null}'
    )
    response = client.chat.completions.create(
        model=settings.GROQ_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.1,
        max_tokens=200,
        response_format={"type": "json_object"},
    )
    data = json.loads(response.choices[0].message.content)
    # Sanitise: only keep valid taxonomy values
    raw_category = str(data.get("category", "all")).lower()
    category = raw_category if raw_category in _VALID_CATEGORIES else "all"
    raw_tags = [str(t).lower() for t in (data.get("tags") or [])]
    tags = [t for t in raw_tags if t in _VALID_TAGS]
    return {
        "category": category,
        "tags": tags,
        "use_case": data.get("use_case"),
    }


def map_attributes(
    message: str,
    session_context: dict[str, Any] | None = None,
    intent: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Translate message/intent to structured catalog attributes using Groq; fallback to parse_user_query."""
    ctx = session_context or {}
    prior_constraints = ctx.get("confirmed_constraints", {})

    # Budget / brand come from intent (already parsed by intent_extraction)
    max_budget = None
    min_budget = None
    brand = None
    if intent:
        max_budget = intent.get("max_budget") or intent.get("budget")
        min_budget = intent.get("min_budget")
        brand = intent.get("brand")
    explicit_constraints = (intent or {}).get("constraints", [])
    implicit_constraints = (intent or {}).get("implicit_constraints", [])

    try:
        groq_result = _call_groq_for_mapping(message, intent, session_context)
        category = groq_result["category"]
        tags = groq_result["tags"]
        use_case = groq_result.get("use_case")

        # Merge implicit_constraints as tags
        for ic in implicit_constraints:
            slug = ic.lower().replace(" ", "-")
            if slug not in tags:
                tags.append(slug)

    except Exception as exc:
        logger.warning("Groq attribute mapping failed (%s); using parse_user_query fallback.", exc)
        fallback = parse_user_query(message, session_context)
        category = fallback.get("category", "all")
        tags = fallback.get("tags", [])
        use_case = fallback.get("use_case")
        if not max_budget:
            max_budget = fallback.get("max_budget")
        if not brand:
            brand = fallback.get("brand")
        # Merge implicit_constraints
        for ic in implicit_constraints:
            slug = ic.lower().replace(" ", "-")
            if slug not in tags:
                tags.append(slug)

    # Prior-turn carry-forward: override only if new message supplies fresh values
    if not category or category == "all":
        category = prior_constraints.get("category", category) or "all"
    if not max_budget:
        max_budget = prior_constraints.get("max_budget")
    if not tags:
        tags = prior_constraints.get("tags", [])

    return {
        "category": category,
        "tags": tags,
        "attributes": tags,
        "use_case": use_case,
        "brand": brand,
        "budget": max_budget,
        "max_budget": max_budget,
        "min_budget": min_budget,
        "explicit_constraints": explicit_constraints,
        "implicit_constraints": implicit_constraints,
    }
