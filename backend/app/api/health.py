from fastapi import APIRouter

from ..config import settings
from ..database import _db_manager

router = APIRouter(prefix="/health", tags=["health"])


@router.get("")
async def health_check() -> dict:
    mongo_status = await _db_manager.ping()
    return {
        "status": "ok",
        "groq_enabled": settings.groq_configured,
        "database": mongo_status,
    }
