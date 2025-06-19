# ========= CRUD 層 =========
# app/crud/attachments.py
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.models.attachments import Attachment
from app.schemas.attachments import AttachmentCreate

async def create_attachment(
    db: AsyncSession, *, user_id: UUID, data: "AttachmentCreate"
) -> Attachment:
    db_obj = Attachment(user_id=user_id, **data.dict())
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj

async def get_attachment(db: AsyncSession, attachment_id: UUID) -> Attachment | None:
    return await db.get(Attachment, attachment_id)

async def list_by_user(db: AsyncSession, user_id: UUID) -> list[Attachment]:
    res = await db.scalars(select(Attachment).where(Attachment.user_id == user_id))
    return list(res)