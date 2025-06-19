# ---------- スキーマ ----------
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

class FeedbackCreate(BaseModel):
    category: str
    message : str

class FeedbackOut(FeedbackCreate):
    id        : UUID
    handled   : str
    created_at: datetime
    class Config:
        orm_mode = True
