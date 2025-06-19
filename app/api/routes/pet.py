# app/api/routes/pet.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.api.dependencies import get_db, get_current_user
from app.services import pet_service
from app.schemas.pet import PetCreate, PetRead, PetUpdate

router = APIRouter()

@router.get("/pets/", response_model=list[PetRead])
async def list_my_pets(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    現在ログインしているユーザーに紐づくペット一覧を返す。
    """
    return await pet_service.get_pets_by_user(db, UUID(current_user["id"]))

@router.post("/pets/", response_model=PetRead)
async def add_pet(
    pet: PetCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    ペット情報を新規登録する。
    """
    return await pet_service.create_pet(db, UUID(current_user["id"]), pet)

@router.put("/pets/{pet_id}", response_model=PetRead)
async def update_pet(
    pet_id: UUID,
    update: PetUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    指定されたペットの情報を更新する。
    """
    updated = await pet_service.update_pet(db, pet_id, update)
    if not updated:
        raise HTTPException(status_code=404, detail="ペットが見つかりません")
    return updated

@router.delete("/pets/{pet_id}")
async def delete_pet(
    pet_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    指定されたペットを削除する。
    """
    deleted = await pet_service.delete_pet(db, pet_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="対象のペットが見つかりません")
    return {"detail": "削除しました"}
