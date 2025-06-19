from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

class APIKeyBase(BaseModel):
    key: str

class APIKeyCreate(APIKeyBase):
    pass

class APIKey(APIKeyBase):
    id: UUID
    user_id: UUID
    is_active: bool
    created_at: datetime

    class Config:
        orm_mode = True
