from __future__ import annotations

import uuid
from typing import Any

from ..agents.attribute_mapping import map_attributes
from ..agents.candidate_retrieval import retrieve_candidates
from ..agents.clarification import determine_clarification
from ..agents.explanation import build_explanation
from ..agents.fallback import build_fallback
from ..agents.intent_extraction import extract_intent
from ..agents.query_ingestion import ingest_query
from ..agents.ranking import rank_candidates
from ..services.product_service import build_recommendation_response


def orchestrate_chat(message: str, user_id: str = "demo-user", session_id: str | None = None) -> dict[str, Any]:
    ingested = ingest_query(message, session_id=session_id, user_id=user_id)
    intent = extract_intent(message)
    mapped = map_attributes(message)
    clarification = determine_clarification(intent)
    if clarification["needs_clarification"]:
        return {
            "session_id": ingested["session_id"],
            "turn_id": uuid.uuid4().hex,
            "assistant_response": "I can help, but I need one more detail to narrow the shortlist.",
            "clarification_question": clarification["question"],
            "needs_clarification": True,
            "intent": intent,
            "constraints": mapped,
            "recommendations": [],
            "confidence": clarification["confidence"],
            "clarification_threshold": clarification["threshold"],
            "pipeline_metadata": {"stages": ["ingest", "intent", "clarification"]},
        }

    constraints = mapped
    products = retrieve_candidates(constraints)
    ranked = rank_candidates(products, constraints)
    recommendations = []
    for product in ranked[:3]:
        score_details = product.get("score_breakdown", {})
        explanation = build_explanation(product, constraints, score_details)
        recommendations.append({
            "product_id": product.get("product_id"),
            "name": product.get("name"),
            "brand": product.get("brand"),
            "category": product.get("category"),
            "price": product.get("price"),
            "currency": product.get("currency"),
            "image": product.get("image"),
            "fit_score": product.get("fit_score"),
            "explanation": explanation,
            "reasons": ["Matches your category and budget"],
            "unmet_constraints": product.get("unmet_constraints", []),
            "stock_status": product.get("stock_status", "in_stock"),
            "match_summary": score_details,
        })

    fallback_payload = build_fallback(message, constraints)
    response = build_recommendation_response(message)
    complementary = response.get("complementary_product")
    return {
        "session_id": ingested["session_id"],
        "turn_id": uuid.uuid4().hex,
        "assistant_response": "Here are the best-fit products based on your query.",
        "clarification_question": None,
        "needs_clarification": False,
        "intent": intent,
        "constraints": constraints,
        "recommendations": recommendations,
        "alternatives": fallback_payload.get("alternatives", []),
        "fallback_details": fallback_payload,
        "complementary_product": complementary,
        "confidence": response.get("confidence", 0.83),
        "clarification_threshold": clarification["threshold"],
        "pipeline_metadata": {
            "stages": ["ingest", "intent", "map_attributes", "retrieve", "rank", "explain", "fallback"],
            "candidate_count": len(products),
            "ranked_count": len(ranked),
        },
    }
