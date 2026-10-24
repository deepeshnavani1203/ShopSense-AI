import os

from dotenv import dotenv_values
from fastapi.testclient import TestClient

from app.config import BACKEND_ENV_FILE, Settings
from app.main import app
from app.services.product_service import build_why_not_response, parse_user_query, rank_products, list_products

client = TestClient(app)


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
