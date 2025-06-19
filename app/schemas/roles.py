from pydantic import BaseModel, ConfigDict
from uuid import UUID

class RoleCreate(BaseModel):
    """
    ロール作成時のリクエストスキーマを定義します。
    """
    slug: str
    name: str

class RoleRead(RoleCreate):
    """
    ロール情報の読み取り用スキーマを定義します。
    """
    id: UUID

    model_config = ConfigDict(from_attributes=True)
