from pydantic import BaseModel
from uuid import UUID

class UserSettingBase(BaseModel):
    receive_notifications: bool = True
    theme: str = "light"

class UserSettingCreate(UserSettingBase):
    pass

class UserSetting(UserSettingBase):
    id: UUID
    user_id: UUID

    class Config:
        orm_mode = True
