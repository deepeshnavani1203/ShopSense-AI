from typing import Any

from fastapi import Depends

from .config import Settings, get_settings


def get_settings_dependency() -> Settings:
    return get_settings()


def get_db_dependency() -> Any:
    return None


def depends_on_settings() -> Any:
    return Depends(get_settings_dependency)


def depends_on_db() -> Any:
    return Depends(get_db_dependency)
