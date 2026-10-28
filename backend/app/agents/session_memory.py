from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

from ..database import get_database

logger = logging.getLogger(__name__)

_SESSION_STORE: dict[str, dict[str, Any]] = {}
_MEM_SESSIONS: dict[str, dict[str, Any]] = {}


# ---------------------------------------------------------------------------
# Async session helpers (MongoDB-backed with in-memory fallback)
# ---------------------------------------------------------------------------

async def get_session(session_id: str) -> dict[str, Any]:
    """Fetch session from MongoDB; fall back to in-memory _MEM_SESSIONS."""
    db = get_database()
    if db is not None:
        try:
            doc = await db["sessions"].find_one({"session_id": session_id})
            if doc:
                doc.pop("_id", None)
                return doc
        except Exception as exc:
            logger.warning("get_session MongoDB error (%s), using in-memory fallback.", type(exc).__name__)
    return _MEM_SESSIONS.get(session_id, {})


async def update_session(session_id: str, user_id: str, turn_data: dict[str, Any]) -> dict[str, Any]:
    """Upsert session document with turn history and constraints."""
    db = get_database()
    now = datetime.utcnow().isoformat()

    turn_entry = turn_data.get("turn_history_entry") or {
        "turn": turn_data.get("turn_number", 1),
        "message": turn_data.get("last_message", ""),
        "response_type": turn_data.get("response_type", "products"),
        "constraints": turn_data.get("confirmed_constraints", {}),
        "timestamp": now,
    }

    if db is not None:
        try:
            existing = await db["sessions"].find_one({"session_id": session_id})
            if existing:
                turns = existing.get("turns", [])
            else:
                turns = []
            turns.append(turn_entry)

            session_doc = {
                "session_id": session_id,
                "user_id": user_id,
                "turns": turns,
                "turn_number": turn_data.get("turn_number", len(turns)),
                "confirmed_constraints": turn_data.get("confirmed_constraints", {}),
                "last_message": turn_data.get("last_message", ""),
                "last_activity": now,
                "title": turn_data.get("last_message", "Shopping session")[:60],
                "query_preview": turn_data.get("last_message", "")[:100],
                "updated_at": now,
                "created_at": existing.get("created_at", now) if existing else now,
            }
            await db["sessions"].update_one(
                {"session_id": session_id},
                {"$set": session_doc},
                upsert=True,
            )
            _MEM_SESSIONS[session_id] = session_doc
            return session_doc
        except Exception as exc:
            logger.warning("update_session MongoDB error (%s), using in-memory fallback.", type(exc).__name__)

    # In-memory fallback
    existing_mem = _MEM_SESSIONS.get(session_id, {})
    turns = existing_mem.get("turns", [])
    turns.append(turn_entry)
    session_doc = {
        "session_id": session_id,
        "user_id": user_id,
        "turns": turns,
        "turn_number": turn_data.get("turn_number", len(turns)),
        "confirmed_constraints": turn_data.get("confirmed_constraints", {}),
        "last_message": turn_data.get("last_message", ""),
        "last_activity": now,
        "title": turn_data.get("last_message", "Shopping session")[:60],
        "query_preview": turn_data.get("last_message", "")[:100],
        "updated_at": now,
        "created_at": existing_mem.get("created_at", now),
    }
    _MEM_SESSIONS[session_id] = session_doc
    return session_doc


async def reset_session(session_id: str) -> dict[str, Any]:
    """Clear session context on explicit topic change."""
    db = get_database()
    if db is not None:
        try:
            await db["sessions"].delete_one({"session_id": session_id})
        except Exception as exc:
            logger.warning("reset_session MongoDB error (%s).", type(exc).__name__)
    _MEM_SESSIONS.pop(session_id, None)
    return {}


# ---------------------------------------------------------------------------
# Sync preference helpers (in-memory; backed by MongoDB in preferences API)
# ---------------------------------------------------------------------------

def get_user_preferences(user_id: str) -> dict[str, Any]:
    return _SESSION_STORE.setdefault(user_id, {"preferences": {}, "sessions": []})


def save_preference(user_id: str, key: str, value: Any) -> dict[str, Any]:
    store = get_user_preferences(user_id)
    store["preferences"][key] = value
    return store


def list_preferences(user_id: str) -> dict[str, Any]:
    return get_user_preferences(user_id).get("preferences", {})


def clear_preference(user_id: str, key: str) -> dict[str, Any]:
    store = get_user_preferences(user_id)
    store["preferences"].pop(key, None)
    return store
