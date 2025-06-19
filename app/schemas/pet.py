# app/schemas/pet.py

from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

# 入力共通の基本情報
class PetBase(BaseModel):
    name: str       # 名前
    species: str    # 種別（犬、猫など）
    breed: str      # 品種（任意）
    age: int        # 年齢

# 作成リクエスト用
class PetCreate(PetBase):
    pass

# 更新リクエスト用
class PetUpdate(PetBase):
    pass

# 応答用（DB取得用）
class PetRead(PetBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True  # SQLAlchemyオブジェクトとの互換有効化
