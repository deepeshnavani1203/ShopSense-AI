from datetime import datetime

from fastapi import APIRouter, HTTPException

from ..database import db_delete_one, db_find_all, db_find_one, db_upsert

router = APIRouter(prefix="/sessions", tags=["sessions"])

# In-memory fallback
_MEM_SESSIONS: dict = {
    "demo-session": {
        "session_id": "demo-session",
        "title": "Starter session",
        "last_activity": "2025-01-01T00:00:00Z",
        "query_preview": "Find comfortable walking shoes under ₹3,000.",
        "turns": [],
        "turn_number": 0,
        "confirmed_constraints": {},
    }
}


@router.get("")
async def list_sessions():
    sessions = await db_find_all("sessions", {})
    if not sessions:
        sessions = list(_MEM_SESSIONS.values())
    return {"sessions": sessions}


@router.post("")
async def create_session(payload: dict):
    now = datetime.utcnow().isoformat()
    session_id = payload.get("session_id") or f"session-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
    session = {
        "session_id": session_id,
        "title": payload.get("title", "New conversation"),
        "last_activity": payload.get("last_activity", now),
        "query_preview": payload.get("query_preview", ""),
        "turns": [],
        "turn_number": 0,
        "confirmed_constraints": {},
        "created_at": now,
        "updated_at": now,
    }
    await db_upsert("sessions", {"session_id": session_id}, session)
    _MEM_SESSIONS[session_id] = session
    return session


@router.get("/{session_id}")
async def get_session(session_id: str):
    doc = await db_find_one("sessions", {"session_id": session_id})
    if not doc:
        doc = _MEM_SESSIONS.get(session_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Session not found")
    return doc


@router.delete("/{session_id}")
async def delete_session(session_id: str):
    deleted = await db_delete_one("sessions", {"session_id": session_id})
    if not deleted:
        if session_id in _MEM_SESSIONS:
            _MEM_SESSIONS.pop(session_id)
        else:
            raise HTTPException(status_code=404, detail="Session not found")
    _MEM_SESSIONS.pop(session_id, None)
    return {"status": "deleted", "session_id": session_id}
