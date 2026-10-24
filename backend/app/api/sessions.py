from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/sessions", tags=["sessions"])

SESSIONS = {
    "demo-session": {
        "session_id": "demo-session",
        "title": "Starter session",
        "last_activity": "2025-01-01T00:00:00Z",
        "query_preview": "Find comfortable walking shoes under ₹3,000.",
    }
}


@router.get("")
async def list_sessions():
    return {"sessions": list(SESSIONS.values())}


@router.post("")
async def create_session(payload: dict):
    session_id = payload.get("session_id", "session-001")
    session = {
        "session_id": session_id,
        "title": payload.get("title", "New conversation"),
        "last_activity": payload.get("last_activity", "2025-01-01T00:00:00Z"),
        "query_preview": payload.get("query_preview", ""),
    }
    SESSIONS[session_id] = session
    return session


@router.get("/{session_id}")
async def get_session(session_id: str):
    if session_id not in SESSIONS:
        raise HTTPException(status_code=404, detail="Session not found")
    return SESSIONS[session_id]


@router.delete("/{session_id}")
async def delete_session(session_id: str):
    if session_id not in SESSIONS:
        raise HTTPException(status_code=404, detail="Session not found")
    SESSIONS.pop(session_id)
    return {"status": "deleted", "session_id": session_id}
