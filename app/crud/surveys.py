from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.survey_submission import SurveySubmission
from app.schemas.survey import SurveyCreate
from typing import List

async def create_survey(db: AsyncSession, survey: SurveyCreate, user_id: str) -> SurveySubmission:
    db_survey = SurveySubmission(user_id=user_id, **survey.dict())
    db.add(db_survey)
    await db.commit()
    await db.refresh(db_survey)
    return db_survey

async def get_surveys(db: AsyncSession, user_id: str) -> List[SurveySubmission]:
    result = await db.execute(select(SurveySubmission).filter(SurveySubmission.user_id == user_id))
    return result.scalars().all()
