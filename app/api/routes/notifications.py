from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from app import crud, schemas
from app.api import deps

router = APIRouter()

@router.post("/", response_model=schemas.Notification)
def create_notification(
    notification_in: schemas.NotificationCreate,
    db: Session = Depends(deps.get_db),
    current_user: schemas.User = Depends(deps.get_current_user),
):
    return crud.crud_notification.create_notification(db, user_id=current_user.id, notification=notification_in)

@router.get("/", response_model=list[schemas.Notification])
def read_notifications(
    db: Session = Depends(deps.get_db),
    current_user: schemas.User = Depends(deps.get_current_user),
):
    return crud.crud_notification.get_notifications_by_user(db, user_id=current_user.id)
