from fastapi import APIRouter, HTTPException

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


@router.post("/why-not")
async def why_not(payload: dict):
    product_id = payload.get("product_id")
    message = payload.get("message", "")
    if not product_id:
        raise HTTPException(status_code=400, detail="product_id is required")
    return build_why_not_response(product_id, message)
