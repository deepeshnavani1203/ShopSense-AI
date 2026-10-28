from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ProductModel(BaseModel):
    product_id: str
    name: str
    brand: str
    category: str
    subcategory: str | None = None
    price: float
    currency: str = "INR"
    description: str
    tags: list[str] = []
    attributes: dict[str, Any] = {}
    use_cases: list[str] = []
    stock_status: str = "in_stock"
    image: str | None = None
    url: str | None = None
    rating: float | None = None
    review_count: int | None = None
    dataset_source: str = "demo"
    created_at: str | None = None
    updated_at: str | None = None


class ProductComparisonRequest(BaseModel):
    product_ids: list[str] = Field(..., min_length=1, max_length=3)


class RecommendationItem(BaseModel):
    product_id: str
    name: str
    brand: str
    category: str
    price: float
    currency: str
    image: str | None = None
    fit_score: float
    explanation: str
    reasons: list[str] = []
    unmet_constraints: list[str] = []
    stock_status: str = "in_stock"
    match_summary: dict[str, Any] = {}


class ChatMessage(BaseModel):
    role: str
    content: str
    timestamp: str | None = None


class ChatRequest(BaseModel):
    user_id: str = "demo-user"
    session_id: str | None = None
    message: str = Field(..., min_length=1, max_length=500)


class DecisionSnapshot(BaseModel):
    turn_number: int = 1
    intent: str = ""
    category: str | None = None
    max_budget: float | None = None
    confidence: float = 0.0
    explicit_constraints: list[dict[str, Any]] = []
    implicit_constraints: list[str] = []
    tags: list[str] = []
    relaxed: str | None = None
    candidate_count: int = 0
    ranked_count: int = 0


class ChatResponse(BaseModel):
    session_id: str
    turn_id: str
    assistant_response: str
    clarification_question: str | None = None
    needs_clarification: bool = False
    response_type: str = "products"  # "products" | "clarification" | "fallback"
    intent: dict[str, Any] = {}
    constraints: dict[str, Any] = {}
    recommendations: list[RecommendationItem] = []
    alternatives: list[RecommendationItem] = []
    fallback_details: dict[str, Any] = {}
    complementary_product: dict[str, Any] | None = None
    confidence: float = 0.0
    clarification_threshold: float = 0.65
    decision_snapshot: dict[str, Any] = {}
    pipeline_metadata: dict[str, Any] = {}


class SessionSummary(BaseModel):
    session_id: str
    title: str
    last_activity: str
    query_preview: str
