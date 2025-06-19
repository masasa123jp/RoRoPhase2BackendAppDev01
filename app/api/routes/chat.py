# app/api/routes/chat.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.dependencies import get_db, get_current_user
from app.schemas.chat import ChatRequest, ChatResponse
from app.utils.openai_client import get_ai_response

router = APIRouter()

@router.post("/chat/completion", response_model=ChatResponse, summary="AIチャット応答")
async def chat_completion(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    ユーザーからのチャットメッセージに対し、OpenAIを使用して応答を返す。
    """
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="メッセージが空です。")

    ai_reply = await get_ai_response(request.message)

    return ChatResponse(
        role="assistant",
        content=ai_reply
    )
