from sqlalchemy.orm import Session
from uuid import UUID

from app.models.user_setting import UserSetting
from app.schemas.user_setting import UserSettingCreate

def create_user_setting(db: Session, user_id: UUID, setting: UserSettingCreate):
    db_setting = UserSetting(user_id=user_id, **setting.dict())
    db.add(db_setting)
    db.commit()
    db.refresh(db_setting)
    return db_setting

def get_user_setting(db: Session, user_id: UUID):
    return db.query(UserSetting).filter(UserSetting.user_id == user_id).first()
