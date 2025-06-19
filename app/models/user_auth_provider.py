from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID, uuid4
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.user import User

class UserAuthProvider(Base):
    """
    外部IDプロバイダーとの関連を管理するモデル。
    """
    __tablename__ = "user_auth_providers"

    # 主キー: UUID
    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)

    # 関連するユーザーのID
    user_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    # プロバイダー名（例: 'google', 'azure_b2c'）
    provider: Mapped[str] = mapped_column(String(32), nullable=False)

    # プロバイダーから提供される一意な識別子（例: sub, oid）
    provider_subject: Mapped[str] = mapped_column(String(255), nullable=False)

    # プロバイダーから取得した生のプロフィール情報（JSON形式）
    raw_profile: Mapped[str] = mapped_column(String, nullable=True)

    # 作成日時
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # ユーザーとのリレーション
    user: Mapped[User] = relationship("User", back_populates="auth_providers")
