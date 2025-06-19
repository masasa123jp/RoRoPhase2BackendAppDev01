from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.utils.validators import validate_upload_file
from app.services.upload_service import save_file_metadata
from app.core.security import get_current_user

router = APIRouter()

@router.post(
    "/upload/",
    summary="ファイルアップロード（認証ユーザーのみ）"
)
async def upload_file(
    file: UploadFile,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    アップロードされたファイルのバリデーションとサニタイジングを実施。
    許可された拡張子・MIMEタイプのみ受け付ける。
    """
    allowed_extensions = [".jpg", ".jpeg", ".png", ".pdf"]
    allowed_mime_types = ["image/jpeg", "image/png", "application/pdf"]
    # ファイル名・MIMEバリデーション
    await validate_upload_file(file, allowed_extensions, allowed_mime_types)
    # ファイル保存＆メタ情報登録
    file_url = await save_file_metadata(db, file, current_user["id"])
    return {"detail": "アップロード成功", "url": file_url}
