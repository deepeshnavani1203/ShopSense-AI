from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/saved-products", tags=["saved-products"])

SAVED = {}


@router.get("")
async def list_saved_products():
    return {"items": SAVED.get("demo-user", [])}


@router.post("")
async def save_product(payload: dict):
    user_id = payload.get("user_id", "demo-user")
    product_id = payload.get("product_id")
    if not product_id:
        raise HTTPException(status_code=400, detail="product_id is required")
    SAVED.setdefault(user_id, [])
    if product_id not in SAVED[user_id]:
        SAVED[user_id].append(product_id)
    return {"items": SAVED[user_id]}


@router.delete("/{product_id}")
async def remove_saved_product(product_id: str):
    user_id = "demo-user"
    if product_id not in SAVED.get(user_id, []):
        raise HTTPException(status_code=404, detail="Saved product not found")
    SAVED[user_id] = [item for item in SAVED[user_id] if item != product_id]
    return {"status": "deleted", "product_id": product_id}
