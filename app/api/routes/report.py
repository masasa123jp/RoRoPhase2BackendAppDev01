# app/api/routes/report.py

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.dependencies import get_db, get_current_user
from app.schemas.report import ReportRequest, ReportResponse
from app.services.report_generator import generate_custom_report

router = APIRouter()

@router.post("/reports/custom", response_model=ReportResponse, summary="カスタムレポート生成")
async def generate_report_custom(
    request: ReportRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    ユーザーとペット情報に基づいてレポートを生成。
    OpenAI連携の有無はリクエストボディのuse_openaiフラグで制御。
    """
    return await generate_custom_report(
        db=db,
        pet_name=request.pet_name,
        species=request.species,
        breed=request.breed,
        age=request.age,
        email=request.email,
        user_id=current_user["id"],
        pet_id=request.pet_id,
        use_openai=request.use_openai
    )
