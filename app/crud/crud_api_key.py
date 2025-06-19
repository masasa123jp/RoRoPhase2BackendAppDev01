from sqlalchemy.orm import Session
from uuid import UUID

from app.models.api_key import APIKey
from app.schemas.api_key import APIKeyCreate

def create_api_key(db: Session, user_id: UUID, api_key: APIKeyCreate):
    db_api_key = APIKey(user_id=user_id, **api_key.dict())
    db.add(db_api_key)
    db.commit()
    db.refresh(db_api_key)
    return db_api_key

def get_api_keys_by_user(db: Session, user_id: UUID):
    return db.query(APIKey).filter(APIKey.user_id == user_id).all()
