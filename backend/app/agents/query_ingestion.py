import re
import uuid
from typing import Any


def ingest_query(message: str, session_id: str | None = None, user_id: str = "demo-user") -> dict[str, Any]:
    cleaned = re.sub(r"\s+", " ", (message or "")).strip()
    if not cleaned:
        raise ValueError("Message is empty.")
    return {
        "session_id": session_id or uuid.uuid4().hex,
        "user_id": user_id,
        "normalized_message": cleaned,
        "original_message": message,
        "turn_number": 1,
    }
