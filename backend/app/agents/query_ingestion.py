from __future__ import annotations

import re
import uuid
from typing import Any


def ingest_query(
    message: str,
    session_id: str | None = None,
    user_id: str = "demo-user",
    session_context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    cleaned = re.sub(r"\s+", " ", (message or "")).strip()
    if not cleaned:
        raise ValueError("Message is empty.")
    ctx = session_context or {}
    turn_number = ctx.get("turn_number", 0) + 1
    confirmed_constraints = ctx.get("confirmed_constraints", {})
    return {
        "session_id": session_id or uuid.uuid4().hex,
        "user_id": user_id,
        "normalized_message": cleaned,
        "original_message": message,
        "turn_number": turn_number,
        "confirmed_constraints": confirmed_constraints,
    }
