from fastapi import APIRouter, HTTPException

from ..agents.orchestrator import orchestrate_chat
from ..schemas.shop import ChatRequest, ChatResponse

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        result = await orchestrate_chat(
            request.message,
            user_id=request.user_id,
            session_id=request.session_id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return ChatResponse(**result)
