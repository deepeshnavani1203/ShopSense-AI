from fastapi import APIRouter, HTTPException

from ..agents.session_memory import clear_preference, list_preferences, save_preference

router = APIRouter(prefix="/preferences", tags=["preferences"])


@router.get("")
async def get_preferences():
    return {"preferences": {"demo-user": list_preferences("demo-user")}}


@router.put("")
async def put_preferences(payload: dict):
    user_id = payload.get("user_id", "demo-user")
    prefs = payload.get("preferences", {})
    for key, value in prefs.items():
        save_preference(user_id, key, value)
    return {"preferences": list_preferences(user_id)}


@router.delete("")
async def delete_preferences(payload: dict):
    user_id = payload.get("user_id", "demo-user")
    key = payload.get("key")
    if not key:
        raise HTTPException(status_code=400, detail="key is required")
    return {"preferences": clear_preference(user_id, key)}
