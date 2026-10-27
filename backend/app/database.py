import logging
from typing import Any

from motor.motor_asyncio import AsyncIOMotorClient

from .config import settings

logger = logging.getLogger(__name__)


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
