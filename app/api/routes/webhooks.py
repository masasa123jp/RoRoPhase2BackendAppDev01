# app/api/routes/webhooks.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from uuid import UUID

from app.api.dependencies import get_db, get_current_user
from app.crud import crud_webhook
from app.schemas.webhook import WebhookCreate, WebhookResponse
from app.models.user import User

router = APIRouter()

# ─────────────────────────────
# 非同期：Webhook登録（URL重複防止）
# ─────────────────────────────
@router.post("/webhooks/", response_model=WebhookResponse, summary="Webhook URL登録")
async def register_webhook(
    webhook: WebhookCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    現在ログイン中のユーザーに対してWebhookを1件登録する。
    同一URLは重複登録不可（既存があればそれを返す）。
    """
    created = await crud_webhook.create_webhook_async(db, current_user.id, webhook)
    return created

# ─────────────────────────────
# 同期：Webhook一覧取得（ユーザー単位）
# ─────────────────────────────
@router.get("/webhooks/", response_model=list[WebhookResponse], summary="Webhook一覧取得")
def read_webhooks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    現在のユーザーが登録済みのWebhook一覧を取得する。
    """
    return crud_webhook.get_webhooks_by_user(db, user_id=current_user.id)
