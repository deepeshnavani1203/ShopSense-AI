# Implementation Plan — PS-12: Conversational Shopping Assistant

> Execution order follows the dependency chain stated in the brief:
> session_memory → database → orchestrator → agents → API routes → frontend.
> Every item leaves the codebase in a buildable, runnable state.
> Verify commands run from `c:\ShopSense\backend` unless stated otherwise.

---

## STEP 1 — session_memory.py: full async MongoDB-backed session persistence

**What:** Replace the current in-memory `_SESSION_STORE` dict with an async MongoDB-backed
session store. Expose three public async functions — `get_session`, `update_session`,
`reset_session` — plus keep the four sync preference helpers (they are used by
`api/preferences.py` and will be re-wired in Step 9). Add an in-memory dict fallback for
when `db` is `None`.

**Design decision:** session documents live in the `sessions` MongoDB collection with the
shape `{session_id, user_id, turn_number, confirmed_constraints, turn_history, last_activity}`.
The in-memory fallback mirrors the same dict shape so the rest of the pipeline is
collection-agnostic.

**Files:** `backend/app/agents/session_memory.py`

**Implementation details:**
- Import `get_database` from `..database`.
- `_MEM_SESSIONS: dict[str, dict]` — module-level fallback dict.
- `async def get_session(session_id: str) -> dict`: fetch from `sessions` collection by
  `session_id`; if not found or db is None, return `_MEM_SESSIONS.get(session_id, {})`.
- `async def update_session(session_id: str, user_id: str, turn_data: dict) -> dict`:
  upsert the session document; increment `turn_number`; append the turn to `turn_history`;
  update `last_activity` with `datetime.utcnow().isoformat()`. In fallback mode, mutate
  `_MEM_SESSIONS`.
- `async def reset_session(session_id: str) -> None`: delete from `sessions` collection
  (or pop from `_MEM_SESSIONS`).
- Keep existing sync helpers `get_user_preferences`, `save_preference`, `list_preferences`,
  `clear_preference` intact — they use the same `_SESSION_STORE` as before (preferences
  and session state are separate concerns until Step 9 re-wires preferences to MongoDB).

**Verify:** `cd backend && python -m pytest tests/test_health_and_logic.py -v`
All existing tests must still pass (no session_memory tests exist yet; correctness is
verified by integration in Step 4).

---

## STEP 2 — database.py: add seed_products_if_empty() and async CRUD helpers

**What:** Extend `database.py` with:
1. `seed_products_if_empty()` — async function that counts documents in the `products`
   collection; if 0, reads `app/seed/products.json` and bulk-inserts into MongoDB.
2. Async CRUD helpers used by later API routes:
   - `async def get_collection(name: str)` — already exists, keep it.
   - `async def db_find_one(collection: str, query: dict) -> dict | None`
   - `async def db_find_all(collection: str, query: dict = {}) -> list[dict]`
   - `async def db_upsert(collection: str, query: dict, data: dict) -> None`
   - `async def db_delete_one(collection: str, query: dict) -> bool`
   - `async def db_insert_many(collection: str, docs: list[dict]) -> int`

**Design decision:** Keep helpers on the module level (not a class method) so every agent
and API route can import them with a single line. Each helper silently returns its safe
default (`None` / `[]` / `False` / `0`) when `db` is `None`, preserving the in-memory
fallback contract already used everywhere.

**Files:** `backend/app/database.py`

**Implementation details:**
- `seed_products_if_empty()`:
  - Call `get_database()`; if None, return immediately (no-op — file-based seed already
    works via `product_service.load_demo_products()`).
  - `count = await db["products"].count_documents({})`.
  - If count == 0: open `SEED_PATH` (import from `product_service` or re-derive as
    `Path(__file__).parents[0] / "seed" / "products.json"`); `json.load`; strip `_id`
    fields if any; `await db["products"].insert_many(docs)`.
- Each helper wraps its Motor call in try/except, logs a warning on failure, returns the
  safe default.

**Verify:** `cd backend && python -m pytest tests/test_health_and_logic.py -v`
All existing tests pass. The `test_database_manager_checks_mongo_objects_against_none`
and `test_database_ping_does_not_expose_driver_error_details` tests are the critical ones.

---

## STEP 3 — main.py: call seed_products_if_empty in startup_event

**What:** Import `seed_products_if_empty` from `.database` and call it inside the existing
`startup_event` async function, after `ensure_database_ready()`.

**Files:** `backend/app/main.py`

**Implementation details:**
```python
from .database import ensure_database_ready, seed_products_if_empty

@app.on_event("startup")
async def startup_event() -> None:
    logger.info("Starting ShopSense AI backend")
    await ensure_database_ready()
    await seed_products_if_empty()
    logger.info("Backend startup complete")
```

**Verify:** `cd backend && python -m pytest tests/test_health_and_logic.py -v`
All existing tests pass (TestClient triggers startup; no error means seed call is safe
with no MongoDB configured).

---

## STEP 4 — query_ingestion.py: add turn_number tracking from session context

**What:** `ingest_query` must accept an optional `session_context` dict (already passed by
the orchestrator) and derive `turn_number` from it rather than hard-coding `1`.

**Design decision:** `turn_number = session_context.get("turn_number", 0) + 1` — simple
increment without requiring an async DB call inside this pure-function agent. The
orchestrator is responsible for loading session_context before calling `ingest_query`.

**Files:** `backend/app/agents/query_ingestion.py`

**Implementation details:**
- New signature:
  ```python
  def ingest_query(
      message: str,
      session_id: str | None = None,
      user_id: str = "demo-user",
      session_context: dict[str, Any] | None = None,
  ) -> dict[str, Any]:
  ```
- `ctx = session_context or {}`.
- `turn_number = ctx.get("turn_number", 0) + 1`.
- `confirmed_constraints = ctx.get("confirmed_constraints", {})` — pass through so
  downstream agents can see prior-turn context.
- Return dict adds `"turn_number": turn_number` and `"confirmed_constraints": confirmed_constraints`.

**Verify:** `cd backend && python -m pytest tests/test_health_and_logic.py -v`
All existing tests pass.

---

## STEP 5 — intent_extraction.py: real Groq LLM call with fallback

**What:** Replace the single `parse_user_query` delegation with a Groq LLM call that
returns structured intent. Fall back to `parse_user_query` on any error.

**Design decision:** Use `groq` SDK's `chat.completions.create` (synchronous path —
matches the current sync orchestrator; Step 12 makes the orchestrator async, at which
point this becomes `await client.chat.completions.acreate`). Keep the function signature
unchanged for now; the orchestrator passes `session_context` in Step 12.

Prompt template (system + user):
- System: "You are a structured intent extractor for an e-commerce shopping assistant.
  Return ONLY valid JSON."
- User: "Extract from this shopping query: `{message}`.
  Return JSON with keys: intent_type (one of: gift, self_use, replacement, comparison),
  explicit_constraints (array of {field, operator, value}),
  implicit_constraints (array of strings),
  category (string or null),
  confidence (float 0-1).
  No markdown, no prose — raw JSON only."

**Files:** `backend/app/agents/intent_extraction.py`

**Implementation details:**
- Import `groq.Groq` and `settings` from `..config`.
- Build `_groq_client` lazily: `Groq(api_key=settings.GROQ_API_KEY) if settings.groq_configured else None`.
- `_call_groq_for_intent(message, session_context)`:
  - If client is None, raise `RuntimeError("Groq not configured")`.
  - Call `client.chat.completions.create(model=settings.GROQ_MODEL, messages=[...],
    temperature=0.1, max_tokens=300)`.
  - Parse `response.choices[0].message.content` as JSON.
  - Return dict with keys: `intent_type`, `explicit_constraints`, `implicit_constraints`,
    `category`, `confidence`.
- `extract_intent(message, session_context=None)`:
  - Try `_call_groq_for_intent(message, session_context)`.
  - On any exception, log a warning and call `parse_user_query(message, session_context)`
    as fallback.
  - Normalise both paths to the return shape:
    ```python
    {
        "purchase_intent": intent_type,          # str
        "category": category,                    # str|None
        "budget": budget,                        # float|None (from explicit_constraints)
        "max_budget": max_budget,                # float|None
        "min_budget": min_budget,                # float|None
        "brand": brand,                          # str|None
        "tags": tags,                            # list[str]
        "attributes": attributes,                # list[str]
        "explicit_constraints": [...],           # NEW — list[dict]
        "implicit_constraints": [...],           # NEW — list[str]
        "confidence": confidence,                # float
    }
    ```
  - Extract budget from `explicit_constraints` where `field == "price"`.

**Verify:** `cd backend && python -m pytest tests/test_health_and_logic.py -v`
Groq is not called during tests (no API key in test env → falls back to `parse_user_query`).
All tests pass.

---

## STEP 6 — clarification.py: Groq LLM completeness scoring with fallback

**What:** Use Groq to score query completeness (0–1) and generate a targeted clarifying
question. Track which questions have already been answered (via `session_context`) to
avoid re-asking.

**Files:** `backend/app/agents/clarification.py`

**Implementation details:**
- Import `groq.Groq` and `settings`; build lazy `_groq_client` same as Step 5.
- `_call_groq_for_clarification(intent, session_context)`:
  - System: "You are a completeness scorer for a shopping assistant. Return ONLY JSON."
  - User: "Intent summary: `{json.dumps(intent)}`.
    Already answered: `{json.dumps(session_context.get('confirmed_constraints', {}))}`.
    Assign a completeness score 0.0–1.0 and, if below threshold, provide ONE clarifying
    question that addresses the single most critical missing attribute.
    Return JSON: {\"completeness\": float, \"question\": string or null}."
  - Parse response, return `{"completeness": float, "question": str | None}`.
- `determine_clarification(intent, threshold=None, session_context=None)`:
  - `final_threshold = threshold or settings.CLARIFICATION_THRESHOLD`.
  - Try Groq call: extract `completeness` and `question`.
  - On exception: compute `confidence = float(intent.get("confidence", 0.0))`; use
    threshold comparison (original logic) to set `needs` and a generic `question`.
  - Return:
    ```python
    {
        "needs_clarification": completeness < final_threshold,
        "confidence": completeness,
        "threshold": final_threshold,
        "question": question if completeness < final_threshold else None,
    }
    ```

**Verify:** `cd backend && python -m pytest tests/test_health_and_logic.py -v`
All tests pass (Groq not called in tests → fallback path used).

---

## STEP 7 — attribute_mapping.py: Groq LLM catalog taxonomy mapping with fallback

**What:** Use Groq to map colloquial terms to catalog taxonomy (category + tags). Fall back
to the existing `CATEGORY_ALIASES` / `TAG_ALIASES` logic from `product_service`.

**Files:** `backend/app/agents/attribute_mapping.py`

**Implementation details:**
- Import `groq.Groq`, `settings`, `CATEGORY_ALIASES`, `TAG_ALIASES` from
  `..services.product_service`.
- `_call_groq_for_mapping(message, intent, session_context)`:
  - System: "You are a catalog taxonomy mapper. Return ONLY JSON."
  - User: "Message: `{message}`. Intent: `{json.dumps(intent)}`.
    Map to: category (one of: footwear, electronics, outdoor, home-kitchen, fitness,
    books, fashion, gifts, all), tags (list of canonical tags from:
    lightweight, comfortable, budget, durable, waterproof, wireless, student, hiking,
    travel, gaming, office, giftable, fitness, running, casual, premium, low-impact,
    joint-support), use_case (string or null).
    Return JSON: {\"category\": str, \"tags\": [str], \"use_case\": str or null}."
  - Parse response.
- `map_attributes(message, session_context=None, intent=None)`:
  - Accept new optional `intent` parameter (passed by orchestrator in Step 12).
  - Try Groq call; on exception fall back to `parse_user_query(message, session_context)`.
  - Merge session `confirmed_constraints.get("category")` as override if present.
  - Return:
    ```python
    {
        "category": category,
        "tags": tags,
        "attributes": tags,   # keep backward compat
        "use_case": use_case,
        "brand": brand,
        "budget": max_budget,
        "max_budget": max_budget,
        "explicit_constraints": intent.get("explicit_constraints", []) if intent else [],
        "implicit_constraints": intent.get("implicit_constraints", []) if intent else [],
    }
    ```

**Verify:** `cd backend && python -m pytest tests/test_health_and_logic.py -v`
All tests pass.

---

## STEP 8 — candidate_retrieval.py: wire to MongoDB with product_service fallback

**What:** Replace the pure in-memory `candidate_filter(list_products(), ...)` with an
async function that queries the MongoDB `products` collection directly. Fall back to
`product_service.list_products()` if MongoDB is unavailable.

**Design decision:** Make `retrieve_candidates` async (matching the async orchestrator
in Step 12). The fallback is immediate — if `db_find_all` returns an empty list AND
`list_products()` has results, use the file-based products.

**Files:** `backend/app/agents/candidate_retrieval.py`

**Implementation details:**
- Import `db_find_all` from `..database`; import `candidate_filter`, `list_products`
  from `..services.product_service`.
- `async def retrieve_candidates(constraints: dict[str, Any]) -> list[dict[str, Any]]`:
  - Build MongoDB query from constraints:
    - If `category` is set and not "all": `{"category": constraints["category"]}`.
    - If `max_budget` is set: add `{"price": {"$lte": max_budget}}`.
    - If `tags` is non-empty: add `{"tags": {"$in": tags}}`.
  - `raw = await db_find_all("products", mongo_query)`.
  - If `raw` is empty: `raw = list_products()` (fallback).
  - Remove `_id` field from each doc (`doc.pop("_id", None)`).
  - Apply `candidate_filter(raw, constraints)` for any residual filtering not done by
    Mongo (e.g. complex tag intersection).
  - Return filtered list.

**Verify:** `cd backend && python -m pytest tests/test_health_and_logic.py -v`
The `test_chat_endpoint_returns_recommendations` test exercises the full path. All pass.

---

## STEP 9 — ranking.py: real per-field scoring with constraint weighting

**What:** Implement a real scoring algorithm directly in `ranking.py` instead of
delegating to `product_service.rank_products`. Explicit constraints outweigh implicit;
partial-match penalty applied; rating signal boost included.

**Design decision:** Keep `product_service.score_product` as a helper (it already computes
the five sub-scores). Ranking.py adds: constraint-weight normalization, partial-match
penalty (−10 per unmet explicit constraint), and returns `fit_score` as a 0–1 float
(not a 0–100 int).

**Files:** `backend/app/agents/ranking.py`

**Implementation details:**
- Import `score_product` from `..services.product_service`.
- `rank_candidates(products, constraints) -> list[dict]`:
  - `explicit = constraints.get("explicit_constraints", [])` (from intent extractor).
  - `implicit_tags = constraints.get("implicit_constraints", [])` (strings).
  - For each product, call `score_product(product, constraints)` → get
    `category_match`, `use_case_fit`, `feature_match`, `budget_fit`, `rating_signal`
    (all 0–100 floats).
  - Weighted base score (0–100):
    ```
    base = (
        category_match   * 0.25 +
        use_case_fit     * 0.25 +
        feature_match    * 0.20 +
        budget_fit       * 0.15 +
        rating_signal    * 0.15
    )
    ```
  - Penalty: for each unmet explicit constraint (in `metrics["unmet_constraints"]`): `−10`.
  - Implicit match bonus: count how many `implicit_tags` appear in
    `product["tags"] + product["use_cases"]`; add `+3` per match (cap at +12).
  - `fit_score_0_1 = round(max(0.0, min(100.0, base - penalty + bonus)) / 100, 4)`.
  - Annotate product with:
    ```python
    {
        **product,
        "fit_score": fit_score_0_1,
        "score_breakdown": {
            "category_match": category_match,
            "use_case_fit": use_case_fit,
            "feature_match": feature_match,
            "budget_fit": budget_fit,
            "rating_signal": rating_signal,
        },
        "unmet_constraints": metrics["unmet_constraints"],
    }
    ```
  - Sort by `fit_score` descending.
  - Return sorted list.

**Verify:** `cd backend && python -m pytest tests/test_health_and_logic.py::test_rank_products_for_hard_constraint_violation -v`
Test passes; `ranked[0]["fit_score"] >= 0` holds.

---

## STEP 10 — explanation.py: Groq LLM per-product explanations with fallback

**What:** Use Groq to generate a plain-language product explanation that references the
specific stated constraints and flags unmet ones. Fall back to `generate_explanation`
from `product_service`.

**Files:** `backend/app/agents/explanation.py`

**Implementation details:**
- Import `groq.Groq`, `settings`, `generate_explanation` from `..services.product_service`.
- Build lazy `_groq_client`.
- `_call_groq_for_explanation(product, constraints, score_details)`:
  - System: "You are a shopping assistant explaining product recommendations."
  - User: "Product: `{product['name']}` ({product['category']}, ₹{product['price']}).
    Shopper constraints: `{json.dumps(constraints)}`.
    Fit scores: `{json.dumps(score_details)}`.
    Unmet constraints: `{product.get('unmet_constraints', [])}`.
    Write 2 sentences. Sentence 1: why this product matches the stated request.
    Sentence 2: flag any unmet constraint or say 'Fully meets all stated requirements.'
    No bullet points, no markdown."
  - Return `response.choices[0].message.content.strip()`.
- `build_explanation(product, constraints, score_details)`:
  - Try Groq call; on exception return `generate_explanation(product, constraints, score_details)`.

**Verify:** `cd backend && python -m pytest tests/test_health_and_logic.py -v`
All tests pass. Groq not called in tests → fallback returns a non-empty string.

---

## STEP 11 — fallback.py: detect low-confidence results and smart constraint relaxation

**What:** Replace the current thin wrapper with real fallback logic: detect empty/low-confidence
result sets, relax the least-important constraint first (budget before core need), return
`fallback_triggered`, `relaxed_constraint`, `alternatives`, and `trade_off_explanation`.

**Files:** `backend/app/agents/fallback.py`

**Implementation details:**
- Imports: `candidate_filter`, `rank_products`, `list_products` from `..services.product_service`.
- Remove the import of `build_recommendation_response` — fallback.py now handles its own
  retrieval.
- `_relaxation_order = ["max_budget", "tags", "category"]` — relax in this order.
- `build_fallback(message, constraints, ranked_products=None) -> dict`:
  - If `ranked_products` is provided and `len(ranked_products) >= 1` and
    `ranked_products[0]["fit_score"] >= 0.4`: return
    `{"fallback_triggered": False, "relaxed_constraint": None, "alternatives": [],
      "trade_off_explanation": None, "original_constraints": constraints, "relaxed_constraints": constraints}`.
  - Otherwise iterate `_relaxation_order`:
    - For `"max_budget"`: new_constraints = `{**constraints, "max_budget": constraints["max_budget"] * 1.3}`
      if budget is set; label = `f"budget relaxed by 30% to ₹{new_max:.0f}"`.
    - For `"tags"`: new_constraints = `{**constraints, "tags": constraints["tags"][:-1]}`
      (drop the last/least-specific tag); label = `f"removed '{dropped_tag}' filter"`.
    - For `"category"`: new_constraints = `{**constraints, "category": "all"}`; label = `"expanded to all categories"`.
    - Retrieve with relaxed constraints: `candidate_filter(list_products(), new_constraints)`.
    - Rank with `rank_products(...)`.
    - If results non-empty: take top 3, break.
  - Return:
    ```python
    {
        "fallback_triggered": True,
        "relaxed_constraint": label,
        "alternatives": [ranked[:3] as RecommendationItem dicts],
        "trade_off_explanation": f"No exact match found. {label}.",
        "original_constraints": constraints,
        "relaxed_constraints": new_constraints,
    }
    ```
  - If no relaxation finds results: return `fallback_triggered=True`, empty alternatives,
    `trade_off_explanation = "No matching products found even after relaxing constraints."`.

**Verify:** `cd backend && python -m pytest tests/test_health_and_logic.py -v`
All tests pass.

---

## STEP 12 — orchestrator.py: full async orchestration with all agents wired

**What:** Rewrite `orchestrate_chat` as `async def orchestrate_chat(...)` wiring all
agents correctly: load session context first, pass it through the pipeline, apply
confidence-gated clarification, generate decision_snapshot, add complementary suggestion
on purchase-ready responses. Keep the sync `orchestrate_chat` name for backward compat
during the API route update in Step 13.

**Files:** `backend/app/agents/orchestrator.py`

**Implementation details:**

Full replacement of `orchestrator.py`:

```python
async def orchestrate_chat(
    message: str,
    user_id: str = "demo-user",
    session_id: str | None = None,
) -> dict[str, Any]:
```

Pipeline steps (in order):

1. **Load session context:**
   ```python
   session_context = await get_session(session_id) if session_id else {}
   ```

2. **Ingest query** (sync, pass session_context):
   ```python
   ingested = ingest_query(message, session_id=session_id or session_context.get("session_id"),
                           user_id=user_id, session_context=session_context)
   effective_session_id = ingested["session_id"]
   ```

3. **Extract intent** (sync with Groq):
   ```python
   intent = extract_intent(message, session_context=session_context)
   ```
   Merge `session_context.get("confirmed_constraints", {})` into intent for carry-forward.

4. **Check clarification** (sync with Groq):
   ```python
   clarification = determine_clarification(intent, session_context=session_context)
   ```
   If `clarification["needs_clarification"]`:
   - Build clarification response dict.
   - Save turn to session: `await update_session(effective_session_id, user_id, {...})`.
   - Return early with `response_type = "clarification"`.

5. **Map attributes** (sync with Groq):
   ```python
   constraints = map_attributes(message, session_context=session_context, intent=intent)
   ```
   Merge prior `session_context.get("confirmed_constraints", {})` — carry forward category,
   budget, tags from previous turns (override only if new message supplies them).

6. **Retrieve candidates** (async):
   ```python
   products = await retrieve_candidates(constraints)
   ```

7. **Rank** (sync):
   ```python
   ranked = rank_candidates(products, constraints)
   ```

8. **Build explanations** (sync, up to top 3):
   ```python
   recommendations = []
   for product in ranked[:3]:
       expl = build_explanation(product, constraints, product.get("score_breakdown", {}))
       recommendations.append({...})  # full RecommendationItem dict shape
   ```

9. **Build fallback** (sync):
   ```python
   fallback_payload = build_fallback(message, constraints, ranked_products=ranked)
   ```
   Set `response_type = "fallback"` if `fallback_payload["fallback_triggered"]` and
   `not recommendations`.

10. **Complementary suggestion:**
    If `recommendations` and not fallback: find one product in same category as top
    recommendation that is NOT already in recommendations list; wrap as
    `{"product_id", "name", "category", "price", "reason": "Complements your selection."}`.

11. **Build decision_snapshot:**
    ```python
    decision_snapshot = {
        "turn_number": ingested["turn_number"],
        "intent": intent["purchase_intent"],
        "category": constraints.get("category"),
        "max_budget": constraints.get("max_budget"),
        "confidence": clarification["confidence"],
        "explicit_constraints": intent.get("explicit_constraints", []),
        "implicit_constraints": intent.get("implicit_constraints", []),
        "tags": constraints.get("tags", []),
        "relaxed": fallback_payload.get("relaxed_constraint"),
        "candidate_count": len(products),
        "ranked_count": len(ranked),
    }
    ```

12. **Persist session:**
    ```python
    await update_session(effective_session_id, user_id, {
        "turn_number": ingested["turn_number"],
        "confirmed_constraints": constraints,
        "last_message": message,
        "last_activity": datetime.utcnow().isoformat(),
        "turn_history_entry": {
            "turn": ingested["turn_number"],
            "message": message,
            "response_type": response_type,
            "constraints": constraints,
        },
    })
    ```

13. **Return** full response dict matching `ChatResponse` schema (including `response_type`
    and `decision_snapshot` — added to schema in Step 14).

**response_type logic:**
- `"clarification"` if `needs_clarification`.
- `"fallback"` if `fallback_payload["fallback_triggered"]` and no recommendations.
- `"products"` otherwise.

**Imports needed:**
```python
from datetime import datetime
from ..agents.session_memory import get_session, update_session
from ..agents.query_ingestion import ingest_query
from ..agents.intent_extraction import extract_intent
from ..agents.clarification import determine_clarification
from ..agents.attribute_mapping import map_attributes
from ..agents.candidate_retrieval import retrieve_candidates
from ..agents.ranking import rank_candidates
from ..agents.explanation import build_explanation
from ..agents.fallback import build_fallback
```

**Verify:** `cd backend && python -m pytest tests/test_health_and_logic.py -v`
`test_chat_endpoint_returns_recommendations` passes. The API route (Step 13) must be
updated to `await` the result before this test passes completely.

---

## STEP 13 — schemas/shop.py: add response_type and DecisionSnapshot

**What:** Add `response_type` field to `ChatResponse` and a `DecisionSnapshot` model.

**Files:** `backend/app/schemas/shop.py`

**Implementation details:**
- Add to `ChatResponse`:
  ```python
  response_type: str = "products"  # "products" | "clarification" | "fallback"
  decision_snapshot: dict[str, Any] = {}
  ```
- Add `DecisionSnapshot` model (used for documentation; actual payload is `dict` in
  `ChatResponse` to keep schema flexible):
  ```python
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
  ```

**Verify:** `cd backend && python -m pytest tests/test_health_and_logic.py -v`
All tests pass — `ChatResponse` is a superset of the existing shape.

---

## STEP 14 — api/chat.py: make async, return response_type and decision_snapshot

**What:** Make the `chat` endpoint call `await orchestrate_chat(...)` and ensure
`response_type` and `decision_snapshot` are included in the response.

**Files:** `backend/app/api/chat.py`

**Implementation details:**
```python
@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        result = await orchestrate_chat(
            request.message, user_id=request.user_id, session_id=request.session_id
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return ChatResponse(**result)
```

**Verify:** `cd backend && python -m pytest tests/test_health_and_logic.py -v`
`test_chat_endpoint_returns_recommendations` must pass with the full async pipeline.

---

## STEP 15 — api/sessions.py: wire GET/DELETE to MongoDB sessions collection

**What:** Replace the hardcoded `SESSIONS` dict with MongoDB-backed reads/deletes via
`db_find_all` and `db_delete_one`. Keep the in-memory fallback so tests pass with no DB.

**Files:** `backend/app/api/sessions.py`

**Design decision:** Sessions are created implicitly by the orchestrator (Step 12) via
`update_session`. The API only needs GET list, GET by id, and DELETE. The `create_session`
POST endpoint stays for backward compat but also upserts via `db_upsert`.

**Implementation details:**
- Replace top-level `SESSIONS` dict with `_MEM_SESSIONS: dict = {"demo-session": {...}}`.
- `list_sessions()`:
  - `raw = await db_find_all("sessions", {})`.
  - If empty, use `list(_MEM_SESSIONS.values())`.
  - Strip `_id`, return `{"sessions": sessions}`.
- `get_session(session_id)`:
  - Try `db_find_one("sessions", {"session_id": session_id})`.
  - Fallback to `_MEM_SESSIONS.get(session_id)`.
  - 404 if still not found.
  - Strip `_id`, return document including `turn_history` array.
- `delete_session(session_id)`:
  - `deleted = await db_delete_one("sessions", {"session_id": session_id})`.
  - If not deleted: pop from `_MEM_SESSIONS`; if still not found: 404.
  - Return `{"status": "deleted", "session_id": session_id}`.
- `create_session(payload)`:
  - Build session dict; `await db_upsert("sessions", {"session_id": sid}, session)`.
  - Mirror to `_MEM_SESSIONS[sid] = session`.
  - Return session.

**Verify:** `cd backend && python -m pytest tests/test_health_and_logic.py -v`
All tests pass.

---

## STEP 16 — api/saved_products.py: wire to MongoDB saved_products collection

**What:** Replace the module-level `SAVED` dict with MongoDB-backed CRUD using the
`saved_products` collection. In-memory dict fallback retained.

**Files:** `backend/app/api/saved_products.py`

**Implementation details:**
- `_MEM_SAVED: dict[str, list[str]] = {}` — fallback.
- `list_saved_products()`:
  - `doc = await db_find_one("saved_products", {"user_id": "demo-user"})`.
  - Return `{"items": doc.get("product_ids", []) if doc else _MEM_SAVED.get("demo-user", [])}`.
- `save_product(payload)`:
  - `user_id = payload.get("user_id", "demo-user")`.
  - `product_id = payload.get("product_id")` — 400 if missing.
  - `doc = await db_find_one("saved_products", {"user_id": user_id}) or {"user_id": user_id, "product_ids": []}`.
  - Append `product_id` if not already in `doc["product_ids"]`.
  - `await db_upsert("saved_products", {"user_id": user_id}, doc)`.
  - Mirror to `_MEM_SAVED`.
  - Return `{"items": doc["product_ids"]}`.
- `remove_saved_product(product_id)`:
  - Load doc; remove product_id; upsert; mirror to `_MEM_SAVED`.
  - 404 if product_id not in list.
  - Return `{"status": "deleted", "product_id": product_id}`.

**Verify:** `cd backend && python -m pytest tests/test_health_and_logic.py -v`
All tests pass.

---

## STEP 17 — api/preferences.py: wire to MongoDB user_preferences collection

**What:** Add MongoDB persistence to GET/PUT preferences. Keep the sync `session_memory`
helpers as the in-memory fallback.

**Files:** `backend/app/api/preferences.py`

**Implementation details:**
- `get_preferences()`:
  - `doc = await db_find_one("user_preferences", {"user_id": "demo-user"})`.
  - `prefs = doc.get("preferences", {}) if doc else list_preferences("demo-user")`.
  - Return `{"preferences": {"demo-user": prefs}}`.
- `put_preferences(payload)`:
  - `user_id = payload.get("user_id", "demo-user")`.
  - Load existing doc; merge new `preferences` dict over it.
  - `await db_upsert("user_preferences", {"user_id": user_id}, {"user_id": user_id, "preferences": merged})`.
  - Also call `save_preference(user_id, k, v)` for each key (keeps in-memory state
    consistent for fallback path).
  - Return `{"preferences": merged}`.
- Add `POST ""` route as an alias for PUT (for frontend `createSession`-style calls):
  ```python
  @router.post("")
  async def post_preferences(payload: dict):
      return await put_preferences(payload)
  ```

**Verify:** `cd backend && python -m pytest tests/test_health_and_logic.py -v`
All tests pass.

---

## STEP 18 — api/recommendations.py: use session constraints in why-not

**What:** Wire `recommendations/why-not` to use session constraints when available,
providing better constraint-failure reporting.

**Files:** `backend/app/api/recommendations.py`

**Implementation details:**
- In `why_not(payload)`:
  - `session_id = payload.get("session_id")`.
  - If `session_id`: `session = await db_find_one("sessions", {"session_id": session_id})`.
  - `session_constraints = session.get("confirmed_constraints", {}) if session else {}`.
  - Merge `session_constraints` with message-derived constraints:
    `effective_message = payload.get("message", "")` — passed to
    `build_why_not_response(product_id, effective_message)` but also inject
    `session_constraints` into the query via a second argument.
  - Update `build_why_not_response` call signature: it already accepts a message string;
    pass the richer merged context by calling `parse_user_query(message, session_constraints)`.
  - No change to the response shape — `build_why_not_response` already returns the full
    `hard_constraint_failures`, `feature_gaps`, etc.

**Verify:** `cd backend && python -m pytest tests/test_health_and_logic.py::test_why_not_response_has_reasoning -v`
Test passes.

---

## STEP 19 — api.js: add deleteSession and confirm all method signatures

**What:** Add `deleteSession(id)` method to the `api` object. Ensure `whyNot` also accepts
an optional `session_id`. No other additions needed — `getProduct(id)` already exists.

**Files:** `src/services/api.js`

**Implementation details:**
Add to the `api` object:
```javascript
deleteSession: (id) => request(`/sessions/${id}`, { method: 'DELETE' }),
```
Extend `whyNot` to optionally include `session_id`:
```javascript
whyNot: (productId, message, sessionId = null) =>
  request('/recommendations/why-not', {
    method: 'POST',
    body: JSON.stringify({ product_id: productId, message, ...(sessionId ? { session_id: sessionId } : {}) }),
  }),
```

**Verify:** `cd c:\ShopSense && npm run build`
Build succeeds with no errors.

---

## STEP 20 — Discover.jsx: full feature wiring

**What:** Wire all unimplemented Discover features: session_id tracking, "New conversation"
reset, inline product detail modal, "Why this product?" modal, "Why NOT?" modal,
clarification banner, fallback diff-view card, numeric confidence on fit score badge,
complementary product card.

**Files:** `src/pages/Discover.jsx`

**Implementation details:**

### State additions
```javascript
const [sessionId, setSessionId] = useState(null)
const [modalProduct, setModalProduct] = useState(null)   // for "View details"
const [whyModal, setWhyModal] = useState(null)           // for "Why NOT?"
const [clarificationQ, setClarificationQ] = useState('') // current clarification question
const [clarificationInput, setClarificationInput] = useState('')
```

### session_id tracking
In `handleSubmit`:
```javascript
const payload = { user_id: userId, message, ...(sessionId ? { session_id: sessionId } : {}) }
const response = await api.chat(payload)
if (!sessionId && response.session_id) setSessionId(response.session_id)
```

### "New conversation" button
```javascript
const handleNewConversation = async () => {
  if (sessionId) {
    try { await api.deleteSession(sessionId) } catch {}
  }
  setSessionId(null)
  setMessages([{ role: 'assistant', content: 'Hi! Tell me what you are shopping for...' }])
  setResults([])
  setMeta({})
  setClarificationQ('')
  setError('')
}
```
Wire `onClick={handleNewConversation}` on the "New conversation" button.

### Clarification banner (replaces error banner for clarification)
In `handleSubmit`, after response:
```javascript
if (response.needs_clarification && response.clarification_question) {
  setClarificationQ(response.clarification_question)
  setError('')           // do NOT put it in the error banner
} else {
  setClarificationQ('')
}
```
Render below the chat window (before the error banner):
```jsx
{clarificationQ && (
  <div className="mt-4 rounded-xl border border-violet-200 bg-violet-50 px-4 py-3">
    <p className="text-sm font-medium text-violet-800">{clarificationQ}</p>
    <div className="mt-2 flex gap-2">
      <input
        value={clarificationInput}
        onChange={e => setClarificationInput(e.target.value)}
        placeholder="Your answer..."
        className="flex-1 rounded-lg border border-violet-200 px-3 py-1.5 text-sm outline-none"
      />
      <button
        type="button"
        onClick={() => { handleSubmit(clarificationInput); setClarificationInput('') }}
        className="rounded-lg bg-violet-600 px-3 py-1.5 text-sm font-medium text-white"
      >
        Answer
      </button>
    </div>
  </div>
)}
```

### Fallback diff-view card
After `results.map(...)` block, render:
```jsx
{meta?.fallback_details?.fallback_triggered && (
  <div className="rounded-2xl border border-amber-200 bg-amber-50 p-4 text-sm">
    <p className="font-semibold text-amber-800">No exact match — here's what changed:</p>
    <div className="mt-2 grid grid-cols-2 gap-3">
      <div className="rounded-xl bg-white p-3">
        <p className="text-xs font-semibold text-slate-500 mb-1">Original</p>
        <pre className="text-xs text-slate-700 whitespace-pre-wrap">
          {JSON.stringify(meta.fallback_details.original_constraints, null, 2)}
        </pre>
      </div>
      <div className="rounded-xl bg-white p-3">
        <p className="text-xs font-semibold text-amber-600 mb-1">Relaxed ↓</p>
        <pre className="text-xs text-slate-700 whitespace-pre-wrap">
          {JSON.stringify(meta.fallback_details.relaxed_constraints, null, 2)}
        </pre>
      </div>
    </div>
    <p className="mt-2 text-amber-700">{meta.fallback_details.trade_off_explanation}</p>
  </div>
)}
```

### Complementary product card
After the fallback diff-view, render:
```jsx
{meta?.complementary_product && (
  <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
    <p className="text-xs font-semibold uppercase tracking-widest text-slate-500 mb-2">
      You might also like
    </p>
    <div className="flex items-center justify-between">
      <div>
        <p className="font-semibold text-slate-900">{meta.complementary_product.name}</p>
        <p className="text-sm text-slate-500">₹{meta.complementary_product.price}</p>
        <p className="text-xs text-slate-500 mt-1">{meta.complementary_product.reason}</p>
      </div>
    </div>
  </div>
)}
```

### Numeric confidence on fit score badge
Change badge from `{product.fit_score || 0} fit score` to:
```jsx
<div className="rounded-full bg-violet-50 px-3 py-1 text-sm font-semibold text-violet-700">
  {typeof product.fit_score === 'number' ? product.fit_score.toFixed(2) : '—'} fit
</div>
```

### Product action buttons
Replace the `['View details', 'Compare', 'Save', 'Why this product?'].map(...)` block
with individual buttons that have proper handlers:
```jsx
<div className="mt-4 flex flex-wrap gap-2">
  <button onClick={() => setModalProduct(product)} ...>View details</button>
  <button onClick={() => handleCompare(product.product_id)} ...>Compare</button>
  <button onClick={() => handleSave(product.product_id)} ...>Save</button>
  <button onClick={() => alert(product.explanation || 'No explanation available.')} ...>
    Why this product?
  </button>
  <button
    onClick={async () => {
      const lastMsg = messages.filter(m => m.role === 'user').at(-1)?.content || ''
      const data = await api.whyNot(product.product_id, lastMsg, sessionId)
      setWhyModal(data)
    }}
    ...
  >
    Why NOT?
  </button>
</div>
```

### Product detail modal (View details)
```jsx
{modalProduct && (
  <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
    <div className="max-w-lg w-full rounded-2xl bg-white p-6 shadow-xl">
      <img src={modalProduct.image} alt={modalProduct.name} className="h-48 w-full rounded-xl object-cover mb-4" />
      <h2 className="text-xl font-bold text-slate-900">{modalProduct.name}</h2>
      <p className="text-sm text-slate-500 mb-2">{modalProduct.brand} · {modalProduct.category}</p>
      <p className="text-sm text-slate-700 mb-3">{modalProduct.explanation}</p>
      <div className="flex flex-wrap gap-2 mb-3">
        {(modalProduct.unmet_constraints || []).map(c => (
          <span key={c} className="rounded-full bg-red-50 px-2 py-1 text-xs text-red-700">{c}</span>
        ))}
      </div>
      <button onClick={() => setModalProduct(null)} className="mt-2 rounded-full bg-slate-900 px-4 py-2 text-sm text-white">
        Close
      </button>
    </div>
  </div>
)}
```

### Why NOT modal
```jsx
{whyModal && (
  <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
    <div className="max-w-md w-full rounded-2xl bg-white p-6 shadow-xl">
      <h2 className="text-lg font-bold text-slate-900 mb-3">Why not {whyModal.name}?</h2>
      {whyModal.hard_constraint_failures?.length > 0 && (
        <div className="mb-2">
          <p className="text-xs font-semibold text-red-600 mb-1">Constraint failures:</p>
          <ul className="list-disc pl-4 text-sm text-slate-700">
            {whyModal.hard_constraint_failures.map(f => <li key={f}>{f}</li>)}
          </ul>
        </div>
      )}
      {whyModal.feature_gaps?.length > 0 && (
        <div className="mb-2">
          <p className="text-xs font-semibold text-amber-600 mb-1">Feature gaps:</p>
          <ul className="list-disc pl-4 text-sm text-slate-700">
            {whyModal.feature_gaps.map(f => <li key={f}>{f}</li>)}
          </ul>
        </div>
      )}
      <p className="text-sm text-slate-500 mt-3">Fit score: {whyModal.matched_score}</p>
      <button onClick={() => setWhyModal(null)} className="mt-4 rounded-full bg-slate-900 px-4 py-2 text-sm text-white">
        Close
      </button>
    </div>
  </div>
)}
```

**Verify:** `cd c:\ShopSense && npm run build`
Build succeeds with no errors.

---

## STEP 21 — Compare.jsx: show per-constraint fit-score breakdown from real data

**What:** Replace hardcoded `88` / `84` fit scores and missing breakdown with real data from
`product.match_summary`. Show the five sub-scores (`category_match`, `use_case_fit`,
`feature_match`, `budget_fit`, `rating_signal`).

**Files:** `src/pages/Compare.jsx`

**Implementation details:**
- Replace the hardcoded fit score row:
  ```jsx
  <div className="flex items-center justify-between rounded-xl bg-slate-50 p-3">
    <span>Fit score</span>
    <span className="font-semibold text-slate-900">
      {product.fit_score != null ? (product.fit_score * 100).toFixed(0) : '—'}
    </span>
  </div>
  ```
  Note: `product.fit_score` comes from the stored `match_summary` of the ranked result;
  the `/products/compare` endpoint returns raw product documents without scoring. The
  compare page receives `selectedCompare` (list of product IDs) and fetches via
  `api.compareProducts(ids)` which hits `/products/compare`. To get fit scores, the
  frontend needs to source them from `localStorage` or pass them via `setSelectedCompare`.

  **Decision:** Store both product ID and its last-known `fit_score` + `match_summary` in
  `selectedCompare`. Change `selectedCompare` shape from `string[]` to
  `{product_id, fit_score?, match_summary?}[]` and update `App.jsx`'s `handleCompare`
  accordingly. The `compareProducts` API still uses just the IDs.

- In `Compare.jsx`, replace the fit score row and add a breakdown section:
  ```jsx
  {/* Fit score from last recommendation run */}
  <div className="flex items-center justify-between rounded-xl bg-slate-50 p-3">
    <span>Fit score</span>
    <span className="font-semibold text-slate-900">
      {selectedEntry?.fit_score != null
        ? (selectedEntry.fit_score * 100).toFixed(0)
        : product.rating ? Math.round(product.rating * 18) : '—'}
    </span>
  </div>
  ```
  Then add a breakdown block below the stock row:
  ```jsx
  {selectedEntry?.match_summary && Object.entries(selectedEntry.match_summary)
    .filter(([k]) => k !== 'unmet_constraints')
    .map(([key, val]) => (
      <div key={key} className="flex items-center justify-between rounded-xl bg-slate-50 p-3">
        <span className="text-xs">{key.replace(/_/g, ' ')}</span>
        <span className="text-xs font-semibold text-violet-700">{val}</span>
      </div>
    ))
  }
  ```

- The `selectedEntry` for each product is derived from `selectedCompare` (now an array
  of objects):
  ```javascript
  const selectedEntry = selectedCompare.find(e => e.product_id === product.product_id)
  ```

- Update `handleCompare` in `Discover.jsx`:
  ```javascript
  const handleCompare = (productId) => {
    const product = results.find(r => r.product_id === productId)
    setSelectedCompare(prev => {
      const already = prev.find(e => e.product_id === productId)
      if (already) return prev
      return [...prev, {
        product_id: productId,
        fit_score: product?.fit_score,
        match_summary: product?.match_summary,
      }].slice(-3)
    })
  }
  ```

- Update `App.jsx` to initialize `selectedCompare` from localStorage with the new shape;
  the `compareProducts` API call uses `selectedCompare.map(e => e.product_id)`.
  In `Compare.jsx`, change `api.compareProducts(selectedCompare)` to
  `api.compareProducts(selectedCompare.map(e => typeof e === 'string' ? e : e.product_id))`.

**Files modified:** `src/pages/Compare.jsx`, `src/pages/Discover.jsx` (handleCompare),
`src/App.jsx` (selectedCompare shape + compareProducts call in Compare.jsx)

**Verify:** `cd c:\ShopSense && npm run build`
Build succeeds.

---

## STEP 22 — SessionHistory.jsx: wire Delete button

**What:** Wire the Delete button `onClick` to call `api.deleteSession(session_id)` then
remove the session from local state.

**Files:** `src/pages/SessionHistory.jsx`

**Implementation details:**
```javascript
const handleDelete = async (sessionId) => {
  try {
    await api.deleteSession(sessionId)
    setSessions(prev => prev.filter(s => s.session_id !== sessionId))
  } catch {
    // silently fail — session may already be gone
  }
}
```
Wire to the Delete button:
```jsx
<button type="button" onClick={() => handleDelete(session.session_id)} ...>
  <Trash2 className="h-4 w-4" />
  Delete
</button>
```

**Verify:** `cd c:\ShopSense && npm run build`
Build succeeds.

---

## STEP 23 — Full integration verification

**What:** Run the full test suite and frontend build to confirm the entire pipeline works
end-to-end.

**Files:** No changes.

**Verify:**
1. `cd backend && python -m pytest tests/ -v` — all tests pass.
2. `cd c:\ShopSense && npm run build` — Vite build exits 0 with no errors.
3. Manual smoke test (if server is accessible): `POST /api/v1/chat` with
   `{"user_id":"demo-user","message":"Find hiking gear under ₹5000"}` returns
   `response_type: "products"`, `recommendations` array, `decision_snapshot` with
   `confidence` and `turn_number`.

---

## Summary of all files modified

| File | Step |
|------|------|
| `backend/app/agents/session_memory.py` | 1 |
| `backend/app/database.py` | 2 |
| `backend/app/main.py` | 3 |
| `backend/app/agents/query_ingestion.py` | 4 |
| `backend/app/agents/intent_extraction.py` | 5 |
| `backend/app/agents/clarification.py` | 6 |
| `backend/app/agents/attribute_mapping.py` | 7 |
| `backend/app/agents/candidate_retrieval.py` | 8 |
| `backend/app/agents/ranking.py` | 9 |
| `backend/app/agents/explanation.py` | 10 |
| `backend/app/agents/fallback.py` | 11 |
| `backend/app/agents/orchestrator.py` | 12 |
| `backend/app/schemas/shop.py` | 13 |
| `backend/app/api/chat.py` | 14 |
| `backend/app/api/sessions.py` | 15 |
| `backend/app/api/saved_products.py` | 16 |
| `backend/app/api/preferences.py` | 17 |
| `backend/app/api/recommendations.py` | 18 |
| `src/services/api.js` | 19 |
| `src/pages/Discover.jsx` | 20 |
| `src/pages/Compare.jsx` + `src/App.jsx` | 21 |
| `src/pages/SessionHistory.jsx` | 22 |

---

## Key design decisions (recorded for implementer reference)

1. **Sync vs async agents:** Groq SDK calls in intent/clarification/attribute/explanation
   agents remain synchronous (using `groq.Groq`, not `AsyncGroq`) to match the current
   sync-inside-async pattern in FastAPI. This avoids needing `asyncio.to_thread` wrappers
   while still being non-blocking at the FastAPI layer since the event loop yields on the
   `await orchestrate_chat(...)` call. Switching to `AsyncGroq` can be done as a follow-up.

2. **session_context carry-forward:** The orchestrator merges prior confirmed_constraints
   into every agent call so that multi-turn context is preserved without any agent needing
   to re-load the session. The constraint merge rule is: new-turn values override old ones
   for matching keys (e.g., updated budget replaces prior budget); non-overlapping keys
   are carried forward as-is.

3. **fit_score as 0–1 float:** Ranking.py returns `fit_score` as a float in [0,1] (e.g.
   `0.83`). The frontend displays it as-is on Discover ("0.83 fit") and multiplied by 100
   as an integer on Compare ("83"). `product_service.score_product` continues to return
   0–100 for backward compat; ranking.py divides by 100.

4. **selectedCompare shape change:** `selectedCompare` changes from `string[]` to
   `{product_id, fit_score?, match_summary?}[]`. Any code that previously used
   `selectedCompare[i]` as a string must use `.product_id`. The localStorage key is kept
   the same (`shopsense-compare`) — the format change is forward-compatible since the new
   shape is JSON-serializable.

5. **MongoDB vs in-memory fallback:** Every DB-touching function is written with a strict
   fallback contract: if `get_database()` returns `None` (no MONGODB_URI configured),
   the function uses the module-level in-memory dict. This ensures the full stack runs
   locally without MongoDB for development and testing.
