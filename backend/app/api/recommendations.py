from fastapi import APIRouter, HTTPException

from ..database import db_find_one
from ..services.product_service import build_recommendation_response, build_why_not_response

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.post("/why-not")
async def why_not(payload: dict):
    product_id = payload.get("product_id")
    message = payload.get("message", "")
    session_id = payload.get("session_id")

    if not product_id:
        raise HTTPException(status_code=400, detail="product_id is required")

    # Enrich with session constraints when available
    session_constraints: dict = {}
    if session_id:
        session = await db_find_one("sessions", {"session_id": session_id})
        if session:
            session_constraints = session.get("confirmed_constraints", {})

    return build_why_not_response(product_id, message, session_constraints)


@router.post("/fallback")
async def fallback(payload: dict):
    message = payload.get("message", "")
    return build_recommendation_response(message, payload.get("session_context") or {})
