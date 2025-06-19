# app/models/pet.py

from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
from uuid import uuid4

from app.core.database import Base

class Pet(Base):
    """
    ペット情報モデル。
    各ペットはユーザー（飼い主）に属し、種別や年齢などの基本情報を持つ。
    """
    __tablename__ = "pets"

    # 主キー: UUID形式のIDを自動生成
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)

    # 外部キー: ユーザーIDに紐づく（1対多）
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    name = Column(String(50), nullable=False)         # ペットの名前
    species = Column(String(30), nullable=False)      # 種別（例: 犬、猫、鳥）
    breed = Column(String(50), nullable=True)         # 品種（任意）
    age = Column(Integer, nullable=False)             # 年齢（整数）

    created_at = Column(DateTime, default=datetime.now)                       # 登録日時
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now) # 更新日時

    # リレーション: Pet → User（親）を参照
    user = relationship("User", back_populates="pets")
