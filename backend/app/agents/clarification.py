from __future__ import annotations

from typing import Any

from ..config import settings


def determine_clarification(intent: dict[str, Any], threshold: float | None = None) -> dict[str, Any]:
    final_threshold = threshold if threshold is not None else settings.CLARIFICATION_THRESHOLD
    confidence = float(intent.get("confidence", 0.0))
    needs = confidence < final_threshold
    return {
        "needs_clarification": needs,
        "confidence": confidence,
        "threshold": final_threshold,
        "question": "Do you want a student-friendly option or a premium pick within your budget?" if needs else None,
    }
