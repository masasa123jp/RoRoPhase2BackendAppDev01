# ========= スキーマ層 =========
# app/schemas/attachments.py
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field

class AttachmentBase(BaseModel):
    filename   : str
    mime_type  : str
    size_bytes : int

class AttachmentCreate(AttachmentBase):
    blob_path: str = Field(description="Blob Storage 内のパス (SAS で生成)")

class Attachment(AttachmentBase):
    id         : UUID
    blob_path  : str
    created_at : datetime

    class Config:
        orm_mode = True