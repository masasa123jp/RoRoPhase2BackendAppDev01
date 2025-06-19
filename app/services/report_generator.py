# app/services/report_generator.py

from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.report import ReportResponse
from app.models.report_log import ReportLog
from uuid import uuid4

from app.utils.pdf_generator import generate_pdf_report
from app.utils.openai_client import get_ai_response

import os

async def generate_custom_report(
    db: AsyncSession,
    pet_name: str,
    species: str,
    breed: str,
    age: str,
    email: str,
    user_id: str,
    pet_id: str,
    use_openai: bool = False  # フラグでOpenAI連携を切り替え可能
) -> ReportResponse:
    """
    ペット情報に基づいてレポートを生成。
    OpenAIの要約、PDF生成、ログ記録に対応。
    """
    report_id = str(uuid4())

    # OpenAIで要約生成（フラグでON/OFF可能）
    prompt = f"{species}の{breed}、年齢{age}歳、名前{pet_name}について健康的な生活アドバイスをください。"
    summary = await get_ai_response(prompt) if use_openai else "OpenAI連携はOFFです。"

    # PDF生成（テンプレートベース）
    pdf_path = generate_pdf_report(pet_name, species, breed, age, summary, report_id)
    relative_pdf_url = pdf_path.replace("./", "/")

    # DBに履歴を記録
    log = ReportLog(
        user_id=user_id,
        pet_id=pet_id,
        summary=summary,
        pdf_path=relative_pdf_url
    )
    db.add(log)
    await db.commit()

    # レスポンス構築
    return ReportResponse(
        report_id=report_id,
        status="completed",
        download_url=relative_pdf_url
    )
