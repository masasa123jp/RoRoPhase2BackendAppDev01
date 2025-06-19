from __future__ import annotations
from typing import TYPE_CHECKING, List
from sqlalchemy import Column, Integer, String, Table, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.core.database import Base

if TYPE_CHECKING:
    from app.models.user import User

# 中間テーブル: ユーザーとロールの多対多関係を定義
user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", ForeignKey("users.id"), primary_key=True),
    Column("role_id", ForeignKey("roles.id"), primary_key=True),
)

class Role(Base):
    """
    ロールモデルを定義します。
    """
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)  # ロールID（主キー）
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)  # ロール名（ユニーク）

    # ロールとユーザーの多対多関係を定義
    users: Mapped[List[User]] = relationship(
        "User",
        secondary=user_roles,
        back_populates="roles",
        lazy="joined",
    )


