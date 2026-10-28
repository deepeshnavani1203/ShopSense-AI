from fastapi import APIRouter, HTTPException

from ..database import db_find_one, db_upsert

router = APIRouter(prefix="/saved-products", tags=["saved-products"])

# In-memory fallback
_MEM_SAVED: dict[str, list[str]] = {}


@router.get("")
async def list_saved_products():
    doc = await db_find_one("saved_products", {"user_id": "demo-user"})
    if doc:
        return {"items": doc.get("product_ids", [])}
    return {"items": _MEM_SAVED.get("demo-user", [])}


@router.post("")
async def save_product(payload: dict):
    user_id = payload.get("user_id", "demo-user")
    product_id = payload.get("product_id")
    if not product_id:
        raise HTTPException(status_code=400, detail="product_id is required")

    doc = await db_find_one("saved_products", {"user_id": user_id})
    if not doc:
        doc = {"user_id": user_id, "product_ids": _MEM_SAVED.get(user_id, [])}

    ids: list[str] = doc.get("product_ids", [])
    if product_id not in ids:
        ids.append(product_id)
    doc["product_ids"] = ids

    await db_upsert("saved_products", {"user_id": user_id}, doc)
    _MEM_SAVED[user_id] = ids
    return {"items": ids}


@router.delete("/{product_id}")
async def remove_saved_product(product_id: str):
    user_id = "demo-user"
    doc = await db_find_one("saved_products", {"user_id": user_id})
    if not doc:
        doc = {"user_id": user_id, "product_ids": _MEM_SAVED.get(user_id, [])}

    ids: list[str] = doc.get("product_ids", [])
    if product_id not in ids:
        raise HTTPException(status_code=404, detail="Saved product not found")

    ids = [i for i in ids if i != product_id]
    doc["product_ids"] = ids
    await db_upsert("saved_products", {"user_id": user_id}, doc)
    _MEM_SAVED[user_id] = ids
    return {"status": "deleted", "product_id": product_id}
