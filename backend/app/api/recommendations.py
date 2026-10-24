from fastapi import APIRouter, HTTPException

from ..services.product_service import build_why_not_response, build_recommendation_response

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.post("/why-not")
async def why_not(payload: dict):
    product_id = payload.get("product_id")
    message = payload.get("message", "")
    if not product_id:
        raise HTTPException(status_code=400, detail="product_id is required")
    return build_why_not_response(product_id, message)


@router.post("/fallback")
async def fallback(payload: dict):
    message = payload.get("message", "")
    return build_recommendation_response(message, payload.get("session_context") or {})
