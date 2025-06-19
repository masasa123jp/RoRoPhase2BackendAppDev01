# app/models/user.py

from __future__ import annotations

from typing import TYPE_CHECKING, List
from uuid import UUID, uuid4
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, Table
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

# Forward reference のための型チェック（循環インポート防止）
if TYPE_CHECKING:
    from app.models.roles import Role
    from app.models.user_auth_provider import UserAuthProvider
    from app.models.user_event_log import UserEventLog
    from app.models.pet import Pet  # 追加：ユーザーが飼育するペットの定義

# ---------------------------------------
# 中間テーブル：ユーザーとロールの多対多関係を定義
# ---------------------------------------
user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", PG_UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True),
    Column("role_id", PG_UUID(as_uuid=True), ForeignKey("roles.id"), primary_key=True),
)

# ---------------------------------------
# ユーザー本体モデル定義
# ---------------------------------------
class User(Base):
    """
    ユーザーモデル：
    - OIDCによる外部認証を前提とした構成
    - ペットとの1:N関係
    - イベントログ、ロール、IDプロバイダーとの関連を持つ
    """
    __tablename__ = "users"

    # 主キー：UUID
    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)

    # メールアドレス（ユニーク必須）
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)

    # 任意の表示名（ニックネームなど）
    display_name: Mapped[str] = mapped_column(String(100), nullable=True)

    # アクティブ状態（論理削除に使用）
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # 作成日時（登録時自動）
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    # 更新日時（更新のたびに自動更新）
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)

    # 最終ログイン日時（Noneの場合は未ログイン）
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # -----------------------------------
    # 関連：ロール（多対多）
    # -----------------------------------
    roles: Mapped[List[Role]] = relationship(
        "Role",
        secondary=user_roles,
        back_populates="users",  # Role側にある users リレーションと対応
        lazy="joined",           # JOINして一括読み込み
    )

    # -----------------------------------
    # 関連：外部IDプロバイダー（1:N）
    # -----------------------------------
    auth_providers: Mapped[List[UserAuthProvider]] = relationship(
        "UserAuthProvider",
        back_populates="user",
        cascade="all, delete-orphan",  # 親が削除されたら子も削除
        lazy="joined",
    )

    # -----------------------------------
    # 関連：ユーザー操作イベントログ（1:N）
    # 例：削除・復元・パスワード変更など
    # -----------------------------------
    event_logs: Mapped[List[UserEventLog]] = relationship(
        "UserEventLog",
        back_populates="user",
        lazy="selectin"  # N+1防止のためselectinロード
    )

    # -----------------------------------
    # 関連：ペット情報（1:N）
    # 例：1ユーザーが複数の犬・猫などを登録
    # -----------------------------------
    pets: Mapped[List[Pet]] = relationship(
        "Pet",
        back_populates="user",           # Petモデルのuserフィールドと連携
        cascade="all, delete-orphan",    # ユーザー削除時にペットも削除
        lazy="selectin"                  # N+1防止（JOINせず効率取得）
    )
