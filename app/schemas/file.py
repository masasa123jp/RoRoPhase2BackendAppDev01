from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime

class FileRead(BaseModel):
    """
    ファイル情報の読み取り用スキーマ。
    """
    id: UUID
    filename: str
    filepath: str
    content_type: str
    uploaded_at: datetime
    user_id: UUID

    model_config = ConfigDict(from_attributes=True)
