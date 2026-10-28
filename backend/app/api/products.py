from fastapi import APIRouter, HTTPException

from ..agents.best_pick import pick_best
from ..schemas.shop import ProductComparisonRequest
from ..services.product_service import build_why_not_response, get_product_by_id, list_products

router = APIRouter(prefix="/products", tags=["products"])


@router.get("")
async def get_products():
    return {"items": list_products()}


@router.get("/{product_id}")
async def get_product(product_id: str):
    product = get_product_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.post("/compare")
async def compare_products(payload: ProductComparisonRequest):
    products = []
    for item in payload.product_ids:
        product = get_product_by_id(item)
        if product:
            products.append(product)
    if not products:
        raise HTTPException(status_code=404, detail="No valid products found")
    return {"items": products}


@router.post("/best-pick")
async def best_pick(payload: dict):
    """Given a list of product_ids and optional constraints, return the single best pick."""
    product_ids = payload.get("product_ids", [])
    constraints = payload.get("constraints", {})
    if not product_ids:
        raise HTTPException(status_code=400, detail="product_ids is required")
    products = [p for pid in product_ids if (p := get_product_by_id(pid))]
    if not products:
        raise HTTPException(status_code=404, detail="No valid products found")
    result = pick_best(products, constraints)
    return result
