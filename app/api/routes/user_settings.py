from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from app import crud, schemas
from app.api import deps

router = APIRouter()

@router.get("/", response_model=schemas.UserSetting)
def read_user_setting(
    db: Session = Depends(deps.get_db),
    current_user: schemas.User = Depends(deps.get_current_user),
):
    setting = crud.crud_user_setting.get_user_setting(db, user_id=current_user.id)
    if not setting:
        raise HTTPException(status_code=404, detail="User setting not found")
    return setting

@router.put("/", response_model=schemas.UserSetting)
def update_user_setting(
    setting_in: schemas.UserSettingCreate,
    db: Session = Depends(deps.get_db),
    current_user: schemas.User = Depends(deps.get_current_user),
):
    return crud.crud_user_setting.create_user_setting(db, user_id=current_user.id, setting=setting_in)
