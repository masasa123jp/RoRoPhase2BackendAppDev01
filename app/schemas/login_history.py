# ---------- スキーマ ----------
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, IPvAnyAddress

class LoginHistoryOut(BaseModel):
    id         : UUID
    ip_address : IPvAnyAddress
    user_agent : str | None
    logged_at  : datetime

    class Config:
        orm_mode = True
