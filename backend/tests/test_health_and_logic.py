import asyncio
import os
from unittest.mock import AsyncMock

from dotenv import dotenv_values
from fastapi.testclient import TestClient

from app.config import BACKEND_ENV_FILE, Settings
from app.database import DatabaseManager
from app.main import app
from app.services.product_service import build_why_not_response, parse_user_query, rank_products, list_products

client = TestClient(app)


class MongoObject:
    def __bool__(self):
        raise AssertionError("MongoDB objects must not be checked for truthiness")


def test_database_manager_checks_mongo_objects_against_none():
    manager = DatabaseManager()
    admin = type("Admin", (), {"command": AsyncMock(return_value={"ok": 1})})()
    manager.client = type("Client", (), {"admin": admin})()

    async def verify():
        status = await manager.ping()
        collection = await manager.get_collection("products")
        return status, collection

    class Database(MongoObject):
        def __getitem__(self, name):
            return name

    manager.db = Database()
    status, collection = asyncio.run(verify())

    assert status["connected"] is True
    assert collection == "products"


def test_database_ping_does_not_expose_driver_error_details():
    manager = DatabaseManager()
    admin = type("Admin", (), {"command": AsyncMock(side_effect=RuntimeError("private connection detail"))})()
    manager.client = type("Client", (), {"admin": admin})()

    class Database(MongoObject):
        pass

    manager.db = Database()
    status = asyncio.run(manager.ping())

    assert status == {
        "connected": False,
        "database": Settings().MONGODB_DATABASE,
        "message": "MongoDB unreachable",
    }


def test_settings_load_backend_env_independent_of_working_directory(tmp_path, monkeypatch):
    env_values = dotenv_values(BACKEND_ENV_FILE)
    monkeypatch.chdir(tmp_path)
    with monkeypatch.context() as patch:
        patch.setattr(os, "environ", {})
        settings = Settings()

    assert settings.MONGODB_DATABASE == env_values["MONGODB_DATABASE"]
    assert settings.FRONTEND_ORIGIN == env_values["FRONTEND_ORIGIN"]


def test_health_endpoint():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"


def test_parse_user_query_budget_and_category():
    result = parse_user_query("Find comfortable walking shoes under ₹3000")
    assert result["category"] == "footwear"
    assert result["max_budget"] == 3000
    assert "comfortable" in result["tags"]


def test_rank_products_for_hard_constraint_violation():
    products = list_products()[:5]
    constraints = {"category": "footwear", "max_budget": 1500, "tags": ["comfortable"]}
    ranked = rank_products(products, constraints)
    assert len(ranked) >= 1
    assert ranked[0]["fit_score"] >= 0


def test_why_not_response_has_reasoning():
    response = build_why_not_response("shoe-002", "Find comfortable walking shoes under ₹2000")
    assert response["status"] != "not_found"
    assert "hard_constraint_failures" in response


def test_chat_endpoint_returns_recommendations():
    response = client.post("/api/v1/chat", json={"user_id": "tester", "message": "Find comfortable walking shoes under ₹3000"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["recommendations"]
    assert payload["assistant_response"]
