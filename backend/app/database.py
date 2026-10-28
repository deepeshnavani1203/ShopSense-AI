from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from motor.motor_asyncio import AsyncIOMotorClient

from .config import settings

logger = logging.getLogger(__name__)

SEED_PATH = Path(__file__).parent / "seed" / "products.json"


class DatabaseManager:
    def __init__(self) -> None:
        self.client: AsyncIOMotorClient | None = None
        self.db = None

    def connect(self) -> None:
        if not settings.mongo_configured:
            self.client = None
            self.db = None
            logger.warning("MongoDB URI not configured; using in-memory fallback storage.")
            return

        try:
            self.client = AsyncIOMotorClient(settings.MONGODB_URI, serverSelectionTimeoutMS=3000)
            self.db = self.client[settings.MONGODB_DATABASE]
            logger.info("MongoDB client initialized; connectivity will be verified by ping.")
        except Exception as exc:  # pragma: no cover - runtime dependency
            logger.warning("MongoDB client initialization failed (%s).", type(exc).__name__)
            self.client = None
            self.db = None

    async def ping(self) -> dict[str, Any]:
        if self.db is None or self.client is None:
            return {"connected": False, "database": None, "message": "MongoDB not configured"}
        try:
            await self.client.admin.command("ping")
            return {"connected": True, "database": settings.MONGODB_DATABASE, "message": "MongoDB reachable"}
        except Exception as exc:  # pragma: no cover - runtime dependency
            logger.warning("MongoDB ping failed (%s).", type(exc).__name__)
            return {"connected": False, "database": settings.MONGODB_DATABASE, "message": "MongoDB unreachable"}

    async def get_collection(self, name: str):
        if self.db is None:
            return None
        return self.db[name]


_db_manager = DatabaseManager()


def get_database():
    return _db_manager.db


async def ensure_database_ready() -> None:
    _db_manager.connect()
    await _db_manager.ping()


# ---------------------------------------------------------------------------
# Async collection accessors
# ---------------------------------------------------------------------------

async def get_sessions_collection():
    db = get_database()
    return db["sessions"] if db is not None else None


async def get_saved_products_collection():
    db = get_database()
    return db["saved_products"] if db is not None else None


async def get_preferences_collection():
    db = get_database()
    return db["user_preferences"] if db is not None else None


async def get_products_collection():
    db = get_database()
    return db["products"] if db is not None else None


# ---------------------------------------------------------------------------
# Generic async CRUD helpers (safe: return defaults when db is None)
# ---------------------------------------------------------------------------

async def db_find_one(collection: str, query: dict[str, Any]) -> dict[str, Any] | None:
    db = get_database()
    if db is None:
        return None
    try:
        doc = await db[collection].find_one(query)
        if doc:
            doc.pop("_id", None)
        return doc
    except Exception as exc:
        logger.warning("db_find_one(%s) failed: %s", collection, type(exc).__name__)
        return None


async def db_find_all(collection: str, query: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    db = get_database()
    if db is None:
        return []
    try:
        cursor = db[collection].find(query or {})
        docs = await cursor.to_list(length=1000)
        for doc in docs:
            doc.pop("_id", None)
        return docs
    except Exception as exc:
        logger.warning("db_find_all(%s) failed: %s", collection, type(exc).__name__)
        return []


async def db_upsert(collection: str, query: dict[str, Any], data: dict[str, Any]) -> None:
    db = get_database()
    if db is None:
        return
    try:
        await db[collection].update_one(query, {"$set": data}, upsert=True)
    except Exception as exc:
        logger.warning("db_upsert(%s) failed: %s", collection, type(exc).__name__)


async def db_delete_one(collection: str, query: dict[str, Any]) -> bool:
    db = get_database()
    if db is None:
        return False
    try:
        result = await db[collection].delete_one(query)
        return result.deleted_count > 0
    except Exception as exc:
        logger.warning("db_delete_one(%s) failed: %s", collection, type(exc).__name__)
        return False


async def db_insert_many(collection: str, docs: list[dict[str, Any]]) -> int:
    db = get_database()
    if db is None:
        return 0
    try:
        result = await db[collection].insert_many(docs)
        return len(result.inserted_ids)
    except Exception as exc:
        logger.warning("db_insert_many(%s) failed: %s", collection, type(exc).__name__)
        return 0


# ---------------------------------------------------------------------------
# Product seeding
# ---------------------------------------------------------------------------

async def seed_products_if_empty() -> None:
    """Insert products.json into MongoDB if the products collection is empty."""
    db = get_database()
    if db is None:
        logger.info("MongoDB not available; skipping product seed (file-based fallback active).")
        return
    try:
        count = await db["products"].count_documents({})
        if count > 0:
            logger.info("Products collection already has %d documents; skipping seed.", count)
            return
        if not SEED_PATH.exists():
            logger.warning("Seed file not found at %s; skipping product seed.", SEED_PATH)
            return
        with open(SEED_PATH, "r", encoding="utf-8") as f:
            docs: list[dict[str, Any]] = json.load(f)
        # Remove _id fields if any to let MongoDB generate them
        for doc in docs:
            doc.pop("_id", None)
        inserted = await db_insert_many("products", docs)
        logger.info("Seeded %d products into MongoDB.", inserted)
    except Exception as exc:
        logger.warning("seed_products_if_empty failed: %s", type(exc).__name__)
