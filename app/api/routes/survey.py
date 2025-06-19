from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.dependencies import get_db, get_current_user
from app.schemas.survey import SurveyCreate, SurveyRead
from app.crud.surveys import create_survey, get_surveys

router = APIRouter()

@router.post("/", response_model=SurveyRead)
async def create_new_survey(
    survey: SurveyCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    return await create_survey(db=db, survey=survey, user_id=current_user["sub"])

@router.get("/", response_model=list[SurveyRead])
async def read_surveys(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    return await get_surveys(db=db, user_id=current_user["sub"])
