from sqlalchemy.orm import Session
from uuid import UUID

from app.models.notification import Notification
from app.schemas.notification import NotificationCreate

def create_notification(db: Session, user_id: UUID, notification: NotificationCreate):
    db_notification = Notification(user_id=user_id, **notification.dict())
    db.add(db_notification)
    db.commit()
    db.refresh(db_notification)
    return db_notification

def get_notifications_by_user(db: Session, user_id: UUID):
    return db.query(Notification).filter(Notification.user_id == user_id).all()
