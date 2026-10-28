from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from ..agents.attribute_mapping import map_attributes
from ..agents.candidate_retrieval import retrieve_candidates
from ..agents.clarification import determine_clarification
from ..agents.explanation import build_explanation
from ..agents.fallback import build_fallback
from ..agents.intent_extraction import extract_intent
from ..agents.query_ingestion import ingest_query
from ..agents.ranking import rank_candidates
from ..agents.session_memory import get_session, update_session
from ..services.product_service import list_products


async def orchestrate_chat(
    message: str,
    user_id: str = "demo-user",
    session_id: str | None = None,
) -> dict[str, Any]:
    # ── 1. Load prior session context ────────────────────────────────────────
    session_context: dict[str, Any] = {}
    if session_id:
        session_context = await get_session(session_id) or {}

    # ── 2. Ingest / normalise query ──────────────────────────────────────────
    ingested = ingest_query(
        message,
        session_id=session_id,
        user_id=user_id,
        session_context=session_context,
    )
    effective_session_id: str = ingested["session_id"]

    # ── 3. Extract intent (Groq LLM with fallback) ───────────────────────────
    intent = extract_intent(message, session_context=session_context)

    # Carry forward prior confirmed constraints into intent where not overridden
    prior = session_context.get("confirmed_constraints", {})
    if not intent.get("category") and prior.get("category"):
        intent["category"] = prior["category"]
    if not intent.get("max_budget") and prior.get("max_budget"):
        intent["max_budget"] = prior["max_budget"]
        intent["budget"] = prior["max_budget"]

    # ── 4. Clarification gate (Groq LLM with fallback) ───────────────────────
    clarification = determine_clarification(intent, session_context=session_context)

    if clarification["needs_clarification"]:
        await update_session(
            effective_session_id,
            user_id,
            {
                "turn_number": ingested["turn_number"],
                "confirmed_constraints": prior,
                "last_message": message,
                "last_activity": datetime.utcnow().isoformat(),
                "response_type": "clarification",
                "turn_history_entry": {
                    "turn": ingested["turn_number"],
                    "message": message,
                    "response_type": "clarification",
                    "constraints": prior,
                    "timestamp": datetime.utcnow().isoformat(),
                },
            },
        )
        return {
            "session_id": effective_session_id,
            "turn_id": uuid.uuid4().hex,
            "assistant_response": (
                "I can help narrow this down — just one quick question first."
            ),
            "clarification_question": clarification["question"],
            "needs_clarification": True,
            "response_type": "clarification",
            "intent": intent,
            "constraints": prior,
            "recommendations": [],
            "alternatives": [],
            "fallback_details": {},
            "complementary_product": None,
            "confidence": clarification["confidence"],
            "clarification_threshold": clarification["threshold"],
            "decision_snapshot": {
                "turn_number": ingested["turn_number"],
                "intent": intent.get("purchase_intent", "self_use"),
                "category": intent.get("category"),
                "max_budget": intent.get("max_budget"),
                "confidence": clarification["confidence"],
                "explicit_constraints": intent.get("constraints", []),
                "implicit_constraints": intent.get("implicit_constraints", []),
                "tags": [],
                "relaxed": None,
                "candidate_count": 0,
                "ranked_count": 0,
            },
            "pipeline_metadata": {
                "stages": ["ingest", "intent", "clarification"],
            },
        }

    # ── 5. Map attributes (Groq LLM with fallback) ───────────────────────────
    constraints = map_attributes(message, session_context=session_context, intent=intent)

    # ── 6. Retrieve candidates (async MongoDB → file fallback) ───────────────
    products = await retrieve_candidates(constraints)

    # ── 7. Rank & score ───────────────────────────────────────────────────────
    ranked = rank_candidates(products, constraints)

    # ── 8. Build per-product explanations (Groq LLM with fallback) ──────────
    recommendations: list[dict[str, Any]] = []
    for product in ranked[:3]:
        score_details = product.get("score_breakdown", {})
        explanation = build_explanation(product, constraints, score_details)
        recommendations.append(
            {
                "product_id": product.get("product_id"),
                "name": product.get("name"),
                "brand": product.get("brand"),
                "category": product.get("category"),
                "price": product.get("price"),
                "currency": product.get("currency", "INR"),
                "image": product.get("image"),
                "fit_score": product.get("fit_score", 0.0),
                "explanation": explanation,
                "reasons": [
                    f"Fit score: {product.get('fit_score', 0.0)}"
                ],
                "unmet_constraints": product.get("unmet_constraints", []),
                "stock_status": product.get("stock_status", "in_stock"),
                "match_summary": score_details,
            }
        )

    # ── 9. Fallback detection & constraint relaxation ─────────────────────────
    fallback_payload = build_fallback(
        message, constraints, ranked_products=ranked
    )

    response_type = "products"
    if fallback_payload["fallback_triggered"] and not recommendations:
        response_type = "fallback"

    # ── 10. Complementary product suggestion ─────────────────────────────────
    complementary: dict[str, Any] | None = None
    if recommendations and response_type == "products":
        top_category = recommendations[0].get("category")
        top_ids = {r["product_id"] for r in recommendations}
        all_products = list_products()
        for p in all_products:
            if (
                p.get("category") == top_category
                and p.get("product_id") not in top_ids
            ):
                complementary = {
                    "product_id": p.get("product_id"),
                    "name": p.get("name"),
                    "category": p.get("category"),
                    "price": p.get("price"),
                    "image": p.get("image"),
                    "reason": "Complements your selection based on category and use case.",
                }
                break

    # ── 11. Decision snapshot ─────────────────────────────────────────────────
    decision_snapshot: dict[str, Any] = {
        "turn_number": ingested["turn_number"],
        "intent": intent.get("purchase_intent", "self_use"),
        "category": constraints.get("category"),
        "max_budget": constraints.get("max_budget"),
        "confidence": clarification["confidence"],
        "explicit_constraints": intent.get("constraints", []),
        "implicit_constraints": intent.get("implicit_constraints", []),
        "tags": constraints.get("tags", []),
        "relaxed": fallback_payload.get("relaxed_constraint"),
        "candidate_count": len(products),
        "ranked_count": len(ranked),
    }

    # ── 12. Persist session ───────────────────────────────────────────────────
    await update_session(
        effective_session_id,
        user_id,
        {
            "turn_number": ingested["turn_number"],
            "confirmed_constraints": constraints,
            "last_message": message,
            "last_activity": datetime.utcnow().isoformat(),
            "response_type": response_type,
            "turn_history_entry": {
                "turn": ingested["turn_number"],
                "message": message,
                "response_type": response_type,
                "constraints": constraints,
                "timestamp": datetime.utcnow().isoformat(),
            },
        },
    )

    # ── 13. Return full response ──────────────────────────────────────────────
    assistant_msg = (
        "Here are the best-fit products based on your query."
        if recommendations
        else "I couldn't find an exact match, but here are some close alternatives."
    )

    return {
        "session_id": effective_session_id,
        "turn_id": uuid.uuid4().hex,
        "assistant_response": assistant_msg,
        "clarification_question": None,
        "needs_clarification": False,
        "response_type": response_type,
        "intent": intent,
        "constraints": constraints,
        "recommendations": recommendations,
        "alternatives": fallback_payload.get("alternatives", []),
        "fallback_details": fallback_payload,
        "complementary_product": complementary,
        "confidence": clarification["confidence"],
        "clarification_threshold": clarification["threshold"],
        "decision_snapshot": decision_snapshot,
        "pipeline_metadata": {
            "stages": [
                "ingest", "intent", "map_attributes",
                "retrieve", "rank", "explain", "fallback",
            ],
            "candidate_count": len(products),
            "ranked_count": len(ranked),
        },
    }
