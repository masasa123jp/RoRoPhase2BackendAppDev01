from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from app import crud, schemas
from app.api import deps

router = APIRouter()

@router.post("/", response_model=schemas.APIKey)
def create_api_key(
    api_key_in: schemas.APIKeyCreate,
    db: Session = Depends(deps.get_db),
    current_user: schemas.User = Depends(deps.get_current_user),
):
    return crud.crud_api_key.create_api_key(db, user_id=current_user.id, api_key=api_key_in)

@router.get("/", response_model=list[schemas.APIKey])
def read_api_keys(
    db: Session = Depends(deps.get_db),
    current_user: schemas.User = Depends(deps.get_current_user),
):
    return crud.crud_api_key.get_api_keys_by_user(db, user_id=current_user.id)
