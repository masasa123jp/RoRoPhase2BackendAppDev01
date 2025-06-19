# app/services/pet_service.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.pet import Pet
from app.schemas.pet import PetCreate, PetUpdate
from uuid import UUID

async def get_pets_by_user(db: AsyncSession, user_id: UUID):
    """
    指定ユーザーが飼っている全ペットを一覧取得する。
    """
    result = await db.execute(select(Pet).where(Pet.user_id == user_id))
    return result.scalars().all()

async def create_pet(db: AsyncSession, user_id: UUID, data: PetCreate):
    """
    新規ペットを登録する。
    指定されたユーザーIDに紐づけて保存。
    """
    pet = Pet(user_id=user_id, **data.dict())
    db.add(pet)
    await db.commit()
    await db.refresh(pet)
    return pet

async def update_pet(db: AsyncSession, pet_id: UUID, data: PetUpdate):
    """
    既存のペット情報を更新する。
    指定された pet_id に一致するレコードを変更。
    """
    result = await db.execute(select(Pet).where(Pet.id == pet_id))
    pet = result.scalar_one_or_none()
    if pet:
        for field, value in data.dict().items():
            setattr(pet, field, value)
        await db.commit()
        await db.refresh(pet)
    return pet

async def delete_pet(db: AsyncSession, pet_id: UUID):
    """
    指定されたペット（pet_id）を削除する。
    存在しない場合は None を返す。
    """
    result = await db.execute(select(Pet).where(Pet.id == pet_id))
    pet = result.scalar_one_or_none()
    if pet:
        await db.delete(pet)
        await db.commit()
    return pet
