# ---------- ルーター ----------
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from ..dependencies import get_db, get_current_user
from ...schemas.feedback import FeedbackCreate, FeedbackOut
from ...crud.feedback import create_feedback, list_feedbacks

router = APIRouter(prefix="/feedback", tags=["Feedback"])

@router.post("/", response_model=FeedbackOut)
async def send_feedback(
    body: FeedbackCreate,
    db : AsyncSession = Depends(get_db),
    user: dict       = Depends(get_current_user),
):
    return await create_feedback(db, UUID(user["sub"]), body)

@router.get("/", response_model=list[FeedbackOut])
async def my_feedback(
    db : AsyncSession = Depends(get_db),
    user: dict       = Depends(get_current_user),
):
    return await list_feedbacks(db, UUID(user["sub"]))
