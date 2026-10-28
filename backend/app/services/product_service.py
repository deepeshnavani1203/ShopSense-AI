from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from ..schemas.shop import ProductModel, RecommendationItem

BASE_DIR = Path(__file__).resolve().parents[1]
SEED_PATH = BASE_DIR / "seed" / "products.json"

CATEGORY_ALIASES = {
    "shoe": "footwear",
    "shoes": "footwear",
    "boot": "footwear",
    "boots": "footwear",
    "laptop": "electronics",
    "laptops": "electronics",
    "headphone": "electronics",
    "headphones": "electronics",
    "hiking": "outdoor",
    "backpack": "outdoor",
    "camera": "electronics",
    "book": "books",
    "books": "books",
    "kettle": "home-kitchen",
    "mixer": "home-kitchen",
    "bottle": "fitness",
    "yoga": "fitness",
    "watch": "fashion",
    "shirt": "fashion",
    "gift": "gifts",
    "speaker": "electronics",
}

TAG_ALIASES = {
    "lightweight": "lightweight",
    "comfortable": "comfortable",
    "affordable": "budget",
    "durable": "durable",
    "waterproof": "waterproof",
    "wireless": "wireless",
    "college": "student",
    "students": "student",
    "hiking": "hiking",
    "travel": "travel",
    "gaming": "gaming",
    "office": "office",
    "gift": "giftable",
    "fitness": "fitness",
    "running": "running",
    "casual": "casual",
    "premium": "premium",
}


def _safe_num(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def _normalise(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "")).strip().lower()


def extract_budget_from_text(text: str) -> dict[str, Any]:
    cleaned = text or ""
    match = re.search(r"(?:rs\.?|inr|₹)\s*(\d+(?:,\d{3})*(?:\.\d+)?)", cleaned, re.IGNORECASE)
    if not match:
        return {"budget": None, "budget_max": None, "currency": "INR"}
    value = float(match.group(1).replace(",", ""))
    return {"budget": value, "budget_max": value, "currency": "INR"}


def parse_user_query(message: str, session_context: dict[str, Any] | None = None) -> dict[str, Any]:
    text = _normalise(message)
    context = session_context or {}
    category = context.get("category")
    for key, val in CATEGORY_ALIASES.items():
        if key in text:
            category = val
            break
    if category is None:
        category = context.get("category", "all")

    budget_info = extract_budget_from_text(message)
    max_price = budget_info.get("budget_max") or context.get("max_budget")
    min_price = context.get("min_budget")

    attributes = []
    tags: list[str] = []
    for alias, canonical in TAG_ALIASES.items():
        if alias in text:
            tags.append(canonical)
            attributes.append(canonical)

    intent = "self_use"
    if "gift" in text:
        intent = "gift"
    elif "compare" in text:
        intent = "comparison"
    elif "replace" in text or "replacement" in text:
        intent = "replacement"

    return {
        "message": message,
        "category": category,
        "budget": budget_info.get("budget"),
        "max_budget": max_price,
        "min_budget": min_price,
        "intent": intent,
        "tags": sorted(set(tags)),
        "attributes": sorted(set(attributes)),
        "use_case": context.get("use_case") or ("student" if "college" in text else "general"),
        "brand": context.get("brand") or None,
        "currency": "INR",
    }


def load_demo_products() -> list[dict[str, Any]]:
    if SEED_PATH.exists():
        with open(SEED_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        if data:
            return data
    return generate_demo_products()


def generate_demo_products() -> list[dict[str, Any]]:
    product_templates = [
        {
            "product_id": "shoe-001",
            "name": "AeroStride Run X",
            "brand": "AeroStride",
            "category": "footwear",
            "subcategory": "running shoes",
            "price": 2999,
            "currency": "INR",
            "description": "Breathable running shoes made for daily city movement and quick fitness routines.",
            "tags": ["running", "lightweight", "comfortable", "sport"],
            "attributes": {"size": "7-10", "color": "black", "weight": "lightweight"},
            "use_cases": ["running", "daily use"],
            "stock_status": "in_stock",
            "image": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?auto=format&fit=crop&w=900&q=80",
            "url": "https://example.com/products/aerostride-run-x",
            "rating": 4.5,
            "review_count": 184,
            "dataset_source": "demo",
        },
        {
            "product_id": "shoe-002",
            "name": "TrailFlex Trek Pro",
            "brand": "TrailFlex",
            "category": "footwear",
            "subcategory": "hiking boots",
            "price": 4599,
            "currency": "INR",
            "description": "Hiking boot with weather-ready upper and durable grip for uneven terrain.",
            "tags": ["hiking", "durable", "waterproof", "outdoor"],
            "attributes": {"size": "6-11", "color": "olive", "waterproof": True},
            "use_cases": ["hiking", "trekking"],
            "stock_status": "limited",
            "image": "https://images.unsplash.com/photo-1525966222134-fcfa99b8ae77?auto=format&fit=crop&w=900&q=80",
            "url": "https://example.com/products/trailflex-trek-pro",
            "rating": 4.6,
            "review_count": 232,
            "dataset_source": "demo",
        },
        {
            "product_id": "shoe-003",
            "name": "CampusEase Slip-On",
            "brand": "CampusEase",
            "category": "footwear",
            "subcategory": "casual shoes",
            "price": 1899,
            "currency": "INR",
            "description": "Easy casual slip-on for regular commuting with moderate support and comfort.",
            "tags": ["casual", "comfortable", "budget"],
            "attributes": {"size": "5-10", "color": "sand"},
            "use_cases": ["commute", "casual"],
            "stock_status": "in_stock",
            "image": "https://images.unsplash.com/photo-1543163521-1bf539c55dd2?auto=format&fit=crop&w=900&q=80",
            "url": "https://example.com/products/campusease-slip-on",
            "rating": 4.2,
            "review_count": 123,
            "dataset_source": "demo",
        },
        {
            "product_id": "laptop-001",
            "name": "NovaBook 14 Air",
            "brand": "NovaBook",
            "category": "electronics",
            "subcategory": "laptop",
            "price": 52999,
            "currency": "INR",
            "description": "Thin and light laptop designed for student work, note-taking, and daily productivity.",
            "tags": ["lightweight", "student", "portable", "office"],
            "attributes": {"ram": "16GB", "storage": "512GB", "weight": "1.2kg"},
            "use_cases": ["college", "work", "daily use"],
            "stock_status": "in_stock",
            "image": "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?auto=format&fit=crop&w=900&q=80",
            "url": "https://example.com/products/novabook-14-air",
            "rating": 4.4,
            "review_count": 311,
            "dataset_source": "demo",
        },
        {
            "product_id": "laptop-002",
            "name": "PeakDrive Pro 15",
            "brand": "PeakDrive",
            "category": "electronics",
            "subcategory": "laptop",
            "price": 68999,
            "currency": "INR",
            "description": "Performance laptop suited for design, editing, and multitasking workloads.",
            "tags": ["premium", "office", "performance"],
            "attributes": {"ram": "32GB", "storage": "1TB", "weight": "1.8kg"},
            "use_cases": ["creative work", "gaming"],
            "stock_status": "in_stock",
            "image": "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?auto=format&fit=crop&w=900&q=80",
            "url": "https://example.com/products/peakdrive-pro-15",
            "rating": 4.7,
            "review_count": 402,
            "dataset_source": "demo",
        },
        {
            "product_id": "laptop-003",
            "name": "StudyLite 13",
            "brand": "StudyLite",
            "category": "electronics",
            "subcategory": "laptop",
            "price": 38999,
            "currency": "INR",
            "description": "Affordable compact laptop for note-taking, browsing, and light productivity.",
            "tags": ["budget", "student", "portable"],
            "attributes": {"ram": "8GB", "storage": "256GB", "weight": "1.1kg"},
            "use_cases": ["college", "study"],
            "stock_status": "in_stock",
            "image": "https://images.unsplash.com/photo-1525547719571-a2d4ac8945e2?auto=format&fit=crop&w=900&q=80",
            "url": "https://example.com/products/studylite-13",
            "rating": 4.1,
            "review_count": 137,
            "dataset_source": "demo",
        },
        {
            "product_id": "outdoor-001",
            "name": "SummitTrail 40L Pack",
            "brand": "SummitTrail",
            "category": "outdoor",
            "subcategory": "backpack",
            "price": 3499,
            "currency": "INR",
            "description": "Lightweight hiking backpack built for day treks and weekend use.",
            "tags": ["hiking", "travel", "durable"],
            "attributes": {"capacity": "40L", "material": "nylon", "waterproof": True},
            "use_cases": ["hiking", "travel"],
            "stock_status": "in_stock",
            "image": "https://images.unsplash.com/photo-1521572267360-ee0c2909d518?auto=format&fit=crop&w=900&q=80",
            "url": "https://example.com/products/summittrail-40l-pack",
            "rating": 4.6,
            "review_count": 56,
            "dataset_source": "demo",
        },
        {
            "product_id": "outdoor-002",
            "name": "ForestCamp Tent 2P",
            "brand": "ForestCamp",
            "category": "outdoor",
            "subcategory": "tent",
            "price": 7499,
            "currency": "INR",
            "description": "Two-person camping tent with compact setup and water-resistant shell.",
            "tags": ["camping", "outdoor", "durable"],
            "attributes": {"capacity": "2 persons", "waterproof": True},
            "use_cases": ["camping", "travel"],
            "stock_status": "limited",
            "image": "https://images.unsplash.com/photo-1504280390367-361c6d9f38f4?auto=format&fit=crop&w=900&q=80",
            "url": "https://example.com/products/forestcamp-tent-2p",
            "rating": 4.3,
            "review_count": 92,
            "dataset_source": "demo",
        },
        {
            "product_id": "fitness-001",
            "name": "FlexCore Yoga Mat",
            "brand": "FlexCore",
            "category": "fitness",
            "subcategory": "yoga",
            "price": 1299,
            "currency": "INR",
            "description": "Comfortable yoga mat with a non-slip finish for home and studio workouts.",
            "tags": ["fitness", "yoga", "comfort"],
            "attributes": {"thickness": "6mm", "material": "TPE"},
            "use_cases": ["fitness", "home exercise"],
            "stock_status": "in_stock",
            "image": "https://images.unsplash.com/photo-1517836357463-d25dfeac3438?auto=format&fit=crop&w=900&q=80",
            "url": "https://example.com/products/flexcore-yoga-mat",
            "rating": 4.4,
            "review_count": 112,
            "dataset_source": "demo",
        },
        {
            "product_id": "fitness-002",
            "name": "PulseBand Smart Watch",
            "brand": "PulseBand",
            "category": "fitness",
            "subcategory": "wearable",
            "price": 4999,
            "currency": "INR",
            "description": "Fitness tracker for heart rate, step goals, and sleep trends.",
            "tags": ["fitness", "health", "tracking"],
            "attributes": {"battery": "7 days", "waterproof": True},
            "use_cases": ["fitness", "daily tracking"],
            "stock_status": "in_stock",
            "image": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?auto=format&fit=crop&w=900&q=80",
            "url": "https://example.com/products/pulseband-smart-watch",
            "rating": 4.2,
            "review_count": 88,
            "dataset_source": "demo",
        },
        {
            "product_id": "kitchen-001",
            "name": "BrewMate Electric Kettle",
            "brand": "BrewMate",
            "category": "home-kitchen",
            "subcategory": "kitchen appliance",
            "price": 2299,
            "currency": "INR",
            "description": "Fast-boil electric kettle with auto shutoff and easy-pour spout.",
            "tags": ["kitchen", "home", "convenience"],
            "attributes": {"capacity": "1.5L", "power": "1500W"},
            "use_cases": ["daily use", "home"],
            "stock_status": "in_stock",
            "image": "https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?auto=format&fit=crop&w=900&q=80",
            "url": "https://example.com/products/brewmate-kettle",
            "rating": 4.5,
            "review_count": 99,
            "dataset_source": "demo",
        },
        {
            "product_id": "kitchen-002",
            "name": "ChefLift Blender Pro",
            "brand": "ChefLift",
            "category": "home-kitchen",
            "subcategory": "blender",
            "price": 3999,
            "currency": "INR",
            "description": "Compact blender for smoothies, shakes, and breakfast prep.",
            "tags": ["kitchen", "smoothie", "daily use"],
            "attributes": {"capacity": "750ml", "power": "1000W"},
            "use_cases": ["home", "breakfast"],
            "stock_status": "limited",
            "image": "https://images.unsplash.com/photo-1556910103-1c02745aae4d?auto=format&fit=crop&w=900&q=80",
            "url": "https://example.com/products/cheflift-blender-pro",
            "rating": 4.4,
            "review_count": 128,
            "dataset_source": "demo",
        },
        {
            "product_id": "book-001",
            "name": "Deep Work",
            "brand": "Penguin",
            "category": "books",
            "subcategory": "productivity",
            "price": 499,
            "currency": "INR",
            "description": "A practical read on focus, distraction, and professional productivity.",
            "tags": ["study", "focus", "productivity"],
            "attributes": {"format": "paperback"},
            "use_cases": ["study", "career"],
            "stock_status": "in_stock",
            "image": "https://images.unsplash.com/photo-1512820790803-83ca734da794?auto=format&fit=crop&w=900&q=80",
            "url": "https://example.com/products/deep-work",
            "rating": 4.7,
            "review_count": 410,
            "dataset_source": "demo",
        },
        {
            "product_id": "book-002",
            "name": "Atomic Habits",
            "brand": "Random House",
            "category": "books",
            "subcategory": "self-improvement",
            "price": 699,
            "currency": "INR",
            "description": "A popular habit-building guide with clear and actionable frameworks.",
            "tags": ["self-improvement", "habits", "motivation"],
            "attributes": {"format": "paperback"},
            "use_cases": ["growth", "discipline"],
            "stock_status": "in_stock",
            "image": "https://images.unsplash.com/photo-1544947950-fa07a98d237f?auto=format&fit=crop&w=900&q=80",
            "url": "https://example.com/products/atomic-habits",
            "rating": 4.8,
            "review_count": 524,
            "dataset_source": "demo",
        },
        {
            "product_id": "fashion-001",
            "name": "UrbanThread Overshirt",
            "brand": "UrbanThread",
            "category": "fashion",
            "subcategory": "outerwear",
            "price": 2499,
            "currency": "INR",
            "description": "Lightweight overshirt for everyday layering in mild weather.",
            "tags": ["casual", "layering", "comfortable"],
            "attributes": {"color": "olive", "material": "cotton"},
            "use_cases": ["daily wear", "travel"],
            "stock_status": "in_stock",
            "image": "https://images.unsplash.com/photo-1521572267360-ee0c2909d518?auto=format&fit=crop&w=900&q=80",
            "url": "https://example.com/products/urbanthread-overshirt",
            "rating": 4.3,
            "review_count": 97,
            "dataset_source": "demo",
        },
        {
            "product_id": "gift-001",
            "name": "Heritage Desk Clock",
            "brand": "MiraWorks",
            "category": "gifts",
            "subcategory": "home decor",
            "price": 1999,
            "currency": "INR",
            "description": "Classic desk clock for gifting and home styling.",
            "tags": ["giftable", "home", "classic"],
            "attributes": {"material": "wood"},
            "use_cases": ["gift", "desk setup"],
            "stock_status": "in_stock",
            "image": "https://images.unsplash.com/photo-1503602642458-232111445657?auto=format&fit=crop&w=900&q=80",
            "url": "https://example.com/products/heritage-desk-clock",
            "rating": 4.7,
            "review_count": 72,
            "dataset_source": "demo",
        },
    ]

    more_products = []
    for i in range(1, 51):
        category = ["electronics", "footwear", "outdoor", "home-kitchen", "fitness", "books", "fashion", "gifts"][i % 8]
        base = {
            "product_id": f"demo-{i:03d}",
            "name": f"Demo Product {i}",
            "brand": ["Aster", "NorthPeak", "Luma", "UrbanNest", "TrailCore", "ValueLane"][i % 6],
            "category": category,
            "subcategory": "general",
            "price": 499 + (i * 277),
            "currency": "INR",
            "description": "A versatile demo product for testing shopping recommendations and ranking logic.",
            "tags": ["general", "demo", category.split("-")[0]],
            "attributes": {"color": ["black", "navy", "olive", "red"][i % 4], "material": "mixed"},
            "use_cases": ["daily use", "travel"],
            "stock_status": "in_stock",
            "image": "https://images.unsplash.com/photo-1524758631624-e2822e304c36?auto=format&fit=crop&w=900&q=80",
            "url": f"https://example.com/products/demo-{i}",
            "rating": 3.7 + (i % 6) * 0.2,
            "review_count": 20 + i * 5,
            "dataset_source": "demo",
        }
        more_products.append(base)

    full = product_templates + more_products
    output = []
    seen = set()
    for item in full:
        key = item["product_id"]
        if key in seen:
            continue
        seen.add(key)
        item["created_at"] = "2025-01-01T00:00:00Z"
        item["updated_at"] = "2025-01-01T00:00:00Z"
        output.append(item)
    with open(SEED_PATH, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    return output


def list_products() -> list[dict[str, Any]]:
    return load_demo_products()


def candidate_filter(products: list[dict[str, Any]], constraints: dict[str, Any]) -> list[dict[str, Any]]:
    category = constraints.get("category")
    max_budget = constraints.get("max_budget")
    tags = set(constraints.get("tags", []))
    results = []
    for product in products:
        if category and category != "all" and product.get("category") != category:
            continue
        if max_budget and float(product.get("price", 0)) > float(max_budget):
            continue
        product_tags = set(product.get("tags", []))
        product_use_cases = set(product.get("use_cases", []))
        if tags and not set(tags).intersection(product_tags.union(product_use_cases)):
            continue
        results.append(product)
    return results


def get_product_by_id(product_id: str) -> dict[str, Any] | None:
    for product in load_demo_products():
        if product.get("product_id") == product_id:
            return product
    return None


def score_product(product: dict[str, Any], constraints: dict[str, Any]) -> dict[str, Any]:
    product_tags = set(product.get("tags", []))
    product_use_cases = set(product.get("use_cases", []))
    requested_tags = set(constraints.get("tags", []))
    category_match = 1.0 if constraints.get("category") in {"all", None, product.get("category")} else 0.0
    use_case_match = 1.0 if not requested_tags else sum(1 for tag in requested_tags if tag in product_tags or tag in product_use_cases) / max(len(requested_tags), 1)
    budget = constraints.get("max_budget")
    price = float(product.get("price", 0.0))
    if budget:
        budget_ratio = min(1.0, float(budget) / max(price, 1.0))
    else:
        budget_ratio = 1.0
    rating_signal = (product.get("rating") or 0.0) / 5.0
    feature_match = sum(1 for tag in requested_tags if tag in product_tags) / max(len(requested_tags), 1) if requested_tags else 0.5
    score = (
        category_match * 25 +
        use_case_match * 25 +
        feature_match * 20 +
        budget_ratio * 15 +
        rating_signal * 15
    )
    score = max(0.0, min(100.0, round(score * 4, 1)))
    unmet = []
    if budget and price > float(budget):
        unmet.append(f"price exceeds budget of ₹{budget}")
    if requested_tags and not requested_tags.intersection(product_tags):
        unmet.append("matching feature tags not available")
    return {
        "fit_score": score,
        "category_match": round(category_match * 100, 1),
        "use_case_fit": round(use_case_match * 100, 1),
        "feature_match": round(feature_match * 100, 1),
        "budget_fit": round(budget_ratio * 100, 1),
        "rating_signal": round(rating_signal * 100, 1),
        "unmet_constraints": unmet,
    }


def rank_products(products: list[dict[str, Any]], constraints: dict[str, Any]) -> list[dict[str, Any]]:
    ranked = []
    for product in products:
        metrics = score_product(product, constraints)
        price = float(product.get("price", 0.0))
        ranked.append({
            **product,
            "fit_score": metrics["fit_score"],
            "score_breakdown": metrics,
            "unmet_constraints": metrics["unmet_constraints"],
            "explanation": generate_explanation(product, constraints, metrics),
        })
    ranked.sort(key=lambda item: item["fit_score"], reverse=True)
    return ranked


def generate_explanation(product: dict[str, Any], constraints: dict[str, Any], metrics: dict[str, Any]) -> str:
    reasons = []
    if constraints.get("max_budget") and float(product.get("price", 0)) <= float(constraints.get("max_budget")):
        reasons.append(f"matches your ₹{constraints.get('max_budget')} budget")
    if constraints.get("category") not in (None, "all") and product.get("category") == constraints.get("category"):
        reasons.append(f"fits the {constraints.get('category')} category")
    if constraints.get("tags"):
        matches = [tag for tag in constraints.get("tags", []) if tag in set(product.get("tags", []))]
        if matches:
            reasons.append(f"matches key preferences like {', '.join(matches[:2])}")
    if not reasons:
        reasons.append("offers a sensible general match for the request")
    return ". ".join(reasons) + f". Overall fit score: {metrics['fit_score']}" + "."


def build_recommendation_response(message: str, session_context: dict[str, Any] | None = None) -> dict[str, Any]:
    constraints = parse_user_query(message, session_context)
    products = load_demo_products()
    candidate_products = candidate_filter(products, constraints)
    ranked = rank_products(candidate_products, constraints) if candidate_products else []

    recommendations = []
    for product in ranked[:3]:
        reasons = []
        for tag in constraints.get("tags", []):
            if tag in set(product.get("tags", [])):
                reasons.append(f"includes {tag}")
        recommendations.append(
            RecommendationItem(
                product_id=str(product.get("product_id")),
                name=product.get("name"),
                brand=product.get("brand"),
                category=product.get("category"),
                price=float(product.get("price", 0.0)),
                currency=str(product.get("currency", "INR")),
                image=product.get("image"),
                fit_score=float(product.get("fit_score", 0.0)),
                explanation=product.get("explanation"),
                reasons=reasons,
                unmet_constraints=product.get("unmet_constraints", []),
                stock_status=product.get("stock_status", "in_stock"),
                match_summary=product.get("score_breakdown", {}),
            ).model_dump(mode="json")
        )

    fallback = []
    if not recommendations:
        fallback = rank_products(products[:10], constraints)[:3]
        if fallback:
            fallback = [RecommendationItem(
                product_id=str(item.get("product_id")),
                name=item.get("name"),
                brand=item.get("brand"),
                category=item.get("category"),
                price=float(item.get("price", 0.0)),
                currency=str(item.get("currency", "INR")),
                image=item.get("image"),
                fit_score=float(item.get("fit_score", 0.0)),
                explanation=item.get("explanation"),
                reasons=[],
                unmet_constraints=item.get("unmet_constraints", []),
                stock_status=item.get("stock_status", "in_stock"),
                match_summary=item.get("score_breakdown", {}),
            ).model_dump(mode="json") for item in fallback]

    complementary = None
    if recommendations:
        first = recommendations[0]
        category = first["category"]
        for product in products:
            if product.get("category") == category and product.get("product_id") != first["product_id"]:
                complementary = {
                    "product_id": product.get("product_id"),
                    "name": product.get("name"),
                    "category": product.get("category"),
                    "price": product.get("price"),
                    "reason": "Complements the selected recommendation.",
                }
                break

    return {
        "intent": {"purchase_intent": constraints.get("intent", "self_use"), "category": constraints.get("category"), "max_budget": constraints.get("max_budget")},
        "constraints": constraints,
        "recommendations": recommendations,
        "alternatives": fallback,
        "complementary_product": complementary,
        "confidence": 0.83 if recommendations else 0.41,
        "fallback_details": {"reason": "No exact match available" if not recommendations else "Exact match found", "relaxed_constraints": []},
    }


def build_why_not_response(
    product_id: str,
    message: str,
    session_constraints: dict[str, Any] | None = None,
) -> dict[str, Any]:
    product = get_product_by_id(product_id)
    if not product:
        return {"status": "not_found", "message": "Product not found"}
    # Merge message-derived constraints with richer session context
    msg_constraints = parse_user_query(message)
    constraints = {**msg_constraints, **(session_constraints or {})}
    # If session has max_budget, use it
    if session_constraints and session_constraints.get("max_budget"):
        constraints["max_budget"] = session_constraints["max_budget"]
    metrics = score_product(product, constraints)
    price = float(product.get("price", 0.0))
    budget = constraints.get("max_budget")
    hard_failures = list(metrics.get("unmet_constraints", []))
    if budget and price > float(budget):
        over_by = price - float(budget)
        failure_msg = f"over budget by ₹{over_by:.0f}"
        if failure_msg not in hard_failures:
            hard_failures.insert(0, failure_msg)
    return {
        "status": "ok",
        "product_id": product_id,
        "name": product.get("name"),
        "budget_exceeded": bool(budget and price > float(budget)),
        "hard_constraint_failures": hard_failures,
        "feature_gaps": [
            tag for tag in constraints.get("tags", [])
            if tag not in set(product.get("tags", []))
        ],
        "matched_score": round(metrics.get("fit_score", 0) / 100, 4)
        if metrics.get("fit_score", 0) > 1
        else metrics.get("fit_score", 0),
        "message": (
            f"{product.get('name')} was not recommended because: "
            + "; ".join(hard_failures)
            if hard_failures
            else f"{product.get('name')} is a reasonable option but ranked lower than the top picks."
        ),
    }
