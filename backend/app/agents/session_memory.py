from __future__ import annotations

from typing import Any

_SESSION_STORE: dict[str, dict[str, Any]] = {}


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
