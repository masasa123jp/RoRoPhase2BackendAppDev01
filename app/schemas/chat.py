# app/schemas/chat.py

from pydantic import BaseModel

class ChatRequest(BaseModel):
    message: str  # ユーザーの入力メッセージ

class ChatResponse(BaseModel):
    role: str = "assistant"  # 応答側のロール
    content: str             # 応答内容
