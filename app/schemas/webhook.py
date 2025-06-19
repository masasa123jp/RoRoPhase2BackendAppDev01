# app/schemas/webhook.py

from pydantic import BaseModel, AnyUrl
from uuid import UUID
from datetime import datetime

# ─────────────────────────────
# 共通ベース：Webhookの基本属性
# ─────────────────────────────
class WebhookBase(BaseModel):
    url: AnyUrl  # 通知先のURL（正当なURL形式を強制）
    event: str   # 対象イベント名（例: report_created）

# ─────────────────────────────
# 作成時に使用：Webhook登録用のスキーマ
# ─────────────────────────────
class WebhookCreate(WebhookBase):
    """
    Webhook登録時の入力形式。
    """
    pass

# ─────────────────────────────
# DB上のWebhookデータ構造を表すスキーマ
# ─────────────────────────────
class Webhook(WebhookBase):
    """
    DB上で保持されるWebhookエンティティ。
    """
    id: UUID             # WebhookのUUID
    user_id: UUID        # 登録ユーザーのID
    is_active: bool      # 有効／無効フラグ
    created_at: datetime # 登録日時

    class Config:
        orm_mode = True  # SQLAlchemyと連携するために必要
