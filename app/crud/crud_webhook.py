# app/crud/crud_webhook.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from sqlalchemy import select
from uuid import UUID

from app.models.webhook import Webhook
from app.schemas.webhook import WebhookCreate

# ─────────────────────────────
# 非同期: URL重複チェックしてWebhookを新規登録または再利用（async版）
# ─────────────────────────────
async def create_webhook_async(db: AsyncSession, user_id: UUID, webhook_in: WebhookCreate) -> Webhook:
    result = await db.execute(
        select(Webhook).where(Webhook.user_id == user_id, Webhook.url == webhook_in.url)
    )
    existing = result.scalar_one_or_none()
    if existing:
        return existing

    webhook = Webhook(user_id=user_id, **webhook_in.dict())
    db.add(webhook)
    await db.commit()
    await db.refresh(webhook)
    return webhook

# ─────────────────────────────
# 同期版: Webhookを作成
# ─────────────────────────────
def create_webhook(db: Session, user_id: UUID, webhook: WebhookCreate):
    """
    同期バージョンのWebhook登録処理。
    """
    existing = db.query(Webhook).filter(
        Webhook.user_id == user_id, Webhook.url == webhook.url
    ).first()
    if existing:
        return existing

    db_webhook = Webhook(user_id=user_id, **webhook.dict())
    db.add(db_webhook)
    db.commit()
    db.refresh(db_webhook)
    return db_webhook

# ─────────────────────────────
# 同期版: 指定ユーザーのWebhook一覧取得
# ─────────────────────────────
def get_webhooks_by_user(db: Session, user_id: UUID):
    return db.query(Webhook).filter(Webhook.user_id == user_id).all()
