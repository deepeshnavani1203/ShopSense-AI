from __future__ import annotations

import json
import logging
from typing import Any

from ..config import settings

logger = logging.getLogger(__name__)

_groq_client = None


def _get_groq_client():
    global _groq_client
    if _groq_client is None and settings.groq_configured:
        try:
            from groq import Groq
            _groq_client = Groq(api_key=settings.GROQ_API_KEY)
        except Exception as exc:
            logger.warning("Failed to initialise Groq client in clarification: %s", exc)
    return _groq_client


def _call_groq_for_clarification(
    intent: dict[str, Any],
    session_context: dict[str, Any] | None,
) -> dict[str, Any]:
    client = _get_groq_client()
    if client is None:
        raise RuntimeError("Groq not configured")

    already_answered = json.dumps(
        (session_context or {}).get("confirmed_constraints", {})
    )
    system_prompt = (
        "You are a completeness scorer for a shopping assistant. "
        "Return ONLY valid JSON with no markdown and no extra keys."
    )
    user_prompt = (
        f"Intent summary: {json.dumps(intent)}.\n"
        f"Already answered (confirmed constraints): {already_answered}.\n"
        "Score completeness 0.0–1.0. If below 0.65, provide ONE clarifying question "
        "targeting the single most critical missing attribute. "
        "Do not ask about anything already answered. "
        'Return JSON: {"completeness": float, "question": string or null}'
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
    return {
        "completeness": float(data.get("completeness", 0.75)),
        "question": data.get("question"),
    }


def determine_clarification(
    intent: dict[str, Any],
    threshold: float | None = None,
    session_context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Score query completeness with Groq; fall back to confidence-based heuristic."""
    final_threshold = threshold if threshold is not None else settings.CLARIFICATION_THRESHOLD

    try:
        result = _call_groq_for_clarification(intent, session_context)
        completeness = result["completeness"]
        question = result["question"]
    except Exception as exc:
        logger.warning("Groq clarification scoring failed (%s); using fallback.", exc)
        completeness = float(intent.get("confidence", 0.75))
        question = (
            "Could you share a bit more — for example, the recipient's age, "
            "a rough budget, or a specific use case?"
            if completeness < final_threshold
            else None
        )

    needs = completeness < final_threshold
    return {
        "needs_clarification": needs,
        "confidence": completeness,
        "threshold": final_threshold,
        "question": question if needs else None,
    }
