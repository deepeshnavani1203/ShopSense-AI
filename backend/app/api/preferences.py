from fastapi import APIRouter, HTTPException

from ..agents.session_memory import list_preferences, save_preference, clear_preference
from ..database import db_find_one, db_upsert

router = APIRouter(prefix="/preferences", tags=["preferences"])


@router.get("")
async def get_preferences():
    doc = await db_find_one("user_preferences", {"user_id": "demo-user"})
    prefs = doc.get("preferences", {}) if doc else list_preferences("demo-user")
    return {"preferences": {"demo-user": prefs}}


@router.put("")
async def put_preferences(payload: dict):
    user_id = payload.get("user_id", "demo-user")
    new_prefs = payload.get("preferences", {})

    # Load existing
    doc = await db_find_one("user_preferences", {"user_id": user_id})
    existing = doc.get("preferences", {}) if doc else list_preferences(user_id)

    # Merge
    merged = {**existing, **new_prefs}

    await db_upsert(
        "user_preferences",
        {"user_id": user_id},
        {"user_id": user_id, "preferences": merged},
    )
    # Keep in-memory state consistent
    for k, v in new_prefs.items():
        save_preference(user_id, k, v)

    return {"preferences": merged}


@router.post("")
async def post_preferences(payload: dict):
    """Alias for PUT — accepts the same payload shape."""
    return await put_preferences(payload)


@router.delete("")
async def delete_preferences(payload: dict):
    user_id = payload.get("user_id", "demo-user")
    key = payload.get("key")
    if not key:
        raise HTTPException(status_code=400, detail="key is required")

    doc = await db_find_one("user_preferences", {"user_id": user_id})
    prefs = doc.get("preferences", {}) if doc else list_preferences(user_id)
    prefs.pop(key, None)

    await db_upsert(
        "user_preferences",
        {"user_id": user_id},
        {"user_id": user_id, "preferences": prefs},
    )
    clear_preference(user_id, key)
    return {"preferences": prefs}
