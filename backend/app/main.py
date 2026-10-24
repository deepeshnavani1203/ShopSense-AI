import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.chat import router as chat_router
from .api.health import router as health_router
from .api.preferences import router as preferences_router
from .api.products import router as products_router
from .api.recommendations import router as recommendations_router
from .api.saved_products import router as saved_products_router
from .api.sessions import router as sessions_router
from .config import settings
from .database import ensure_database_ready

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("shopsense")

app = FastAPI(title="ShopSense AI", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_ORIGIN, "http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router, prefix="/api/v1")
app.include_router(chat_router, prefix="/api/v1")
app.include_router(sessions_router, prefix="/api/v1")
app.include_router(products_router, prefix="/api/v1")
app.include_router(recommendations_router, prefix="/api/v1")
app.include_router(preferences_router, prefix="/api/v1")
app.include_router(saved_products_router, prefix="/api/v1")


@app.on_event("startup")
async def startup_event() -> None:
    logger.info("Starting ShopSense AI backend")
    await ensure_database_ready()
    logger.info("Backend startup complete")


@app.get("/")
async def root() -> dict:
    return {"message": "ShopSense AI backend is running."}
