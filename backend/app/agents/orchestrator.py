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

    # Don't block with clarification if user provided category, subcategory, budget or tags
    has_meaningful_intent = bool(
        intent.get("category")
        or intent.get("budget")
        or intent.get("max_budget")
        or intent.get("tags")
        or intent.get("subcategory")
    )
    if has_meaningful_intent:
        clarification["needs_clarification"] = False

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
    # Return top 16 so the user has at least 10-15 items to compare
    recommendations: list[dict[str, Any]] = []
    for product in ranked[:16]:
        score_details = product.get("score_breakdown", {})
        explanation = build_explanation(product, constraints, score_details)
        recommendations.append(
            {
                "product_id": product.get("product_id"),
                "name": product.get("name"),
                "brand": product.get("brand"),
                "category": product.get("category"),
                "subcategory": product.get("subcategory"),
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
                "attributes": product.get("attributes", {}),
                "tags": product.get("tags", []),
                "rating": product.get("rating", 4.4),
                "review_count": product.get("review_count", 150),
            }
        )

    # ── 9. Fallback detection & constraint relaxation ─────────────────────────
    fallback_payload = build_fallback(
        message, constraints, ranked_products=ranked
    )

    response_type = "products"
    if fallback_payload["fallback_triggered"] and not recommendations:
        response_type = "fallback"

    # ── 10. Rich "You May Also Like" & Complementary product suggestions ─────
    you_may_also_like: list[dict[str, Any]] = []
    top_ids = {r["product_id"] for r in recommendations}
    budget = constraints.get("max_budget")
    all_products = list_products()

    # 1. Smart Upgrade Pick (e.g. searching laptop with 50k budget -> suggest 60k laptop with better specs)
    if recommendations and budget:
        first = recommendations[0]
        cat = first.get("category")
        subcat = first.get("subcategory") or constraints.get("subcategory")
        upgrade_candidates = [
            p for p in all_products
            if p.get("product_id") not in top_ids
            and (p.get("category") == cat or (subcat and p.get("subcategory") == subcat))
            and float(p.get("price", 0)) > float(budget)
            and float(p.get("price", 0)) <= float(budget) * 1.45
        ]
        upgrade_candidates.sort(key=lambda x: x.get("rating", 0), reverse=True)
        if upgrade_candidates:
            up = upgrade_candidates[0]
            diff = int(float(up.get("price", 0)) - float(budget))
            you_may_also_like.append({
                **up,
                "recommendation_type": "upgrade",
                "badge": f"🚀 Smart Upgrade (+₹{diff:,})",
                "reason": f"Priced slightly above budget at ₹{up.get('price'):,}, but gives you higher memory, faster processor & future-proofing.",
            })
            top_ids.add(up.get("product_id"))

    # 2. Companion Accessories / Pairings
    if recommendations:
        first = recommendations[0]
        cat = first.get("category")
        subcat = first.get("subcategory") or constraints.get("subcategory")
        companion_map = {
            "laptop": ("electronics", "mouse", "Ergonomic productivity accessory for your laptop setup."),
            "phone": ("electronics", "headphone", "Wireless audio companion for crystal clear calls & music."),
            "running shoes": ("fitness", "recovery", "Post-run muscle recovery roller."),
            "hiking boots": ("outdoor", "backpack", "Trail-ready expedition backpack companion."),
            "wallets": ("wallets", "cardholder", "Ultra-slim companion cardholder."),
        }
        target_pair = companion_map.get(subcat or cat)
        if target_pair:
            t_cat, t_subcat, reason = target_pair
            matches = [
                p for p in all_products
                if p.get("product_id") not in top_ids
                and p.get("category") == t_cat
                and p.get("subcategory") == t_subcat
            ]
            if matches:
                comp = matches[0]
                you_may_also_like.append({
                    **comp,
                    "recommendation_type": "companion",
                    "badge": "⚡ Perfect Companion",
                    "reason": reason,
                })
                top_ids.add(comp.get("product_id"))

    # Fallback to general related product if still empty
    if not you_may_also_like and recommendations:
        first = recommendations[0]
        cat = first.get("category")
        for p in all_products:
            if p.get("category") == cat and p.get("product_id") not in top_ids:
                you_may_also_like.append({
                    **p,
                    "recommendation_type": "companion",
                    "badge": "✨ Popular Pick",
                    "reason": f"Popular in {cat} with high customer satisfaction.",
                })
                break

    complementary = you_may_also_like[0] if you_may_also_like else None

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
        "you_may_also_like": you_may_also_like,
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
