# ---------- CRUD ----------
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import select
from app.models.feedback import Feedback
from app.schemas.feedback import FeedbackCreate

async def create_feedback(db: AsyncSession, user_id: UUID, data: FeedbackCreate):
    obj = Feedback(user_id=user_id, **data.dict())
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj

async def list_feedbacks(db: AsyncSession, user_id: UUID):
    rows = await db.scalars(select(Feedback).where(Feedback.user_id == user_id))
    return list(rows)
