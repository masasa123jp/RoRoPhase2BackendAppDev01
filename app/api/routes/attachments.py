# ========= ルーター層 =========
# app/api/routes/attachments.py
from fastapi import APIRouter, Depends, UploadFile, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from ..dependencies import get_db, get_current_user
from ...schemas.attachments import Attachment, AttachmentCreate
from ...crud.attachments import create_attachment, list_by_user, get_attachment
from ...utils.blob_storage import save_to_blob  # 既存 util: ファイルを Blob に保存しパス返却

router = APIRouter(prefix="/attachments", tags=["Attachment"])

@router.post("/", response_model=Attachment)
async def upload_file(
    file: UploadFile,
    db : AsyncSession     = Depends(get_db),
    user: dict            = Depends(get_current_user),
):
    """ファイルを受け取り Blob へ保存、メタ情報を DB 登録"""
    blob_path = await save_to_blob(file)          # 例: "reports/uuid-filename"
    data = AttachmentCreate(
        filename=file.filename,
        mime_type=file.content_type or "application/octet-stream",
        size_bytes=len(await file.read()),
        blob_path=blob_path,
    )
    return await create_attachment(db, user_id=UUID(user["sub"]), data=data)

@router.get("/", response_model=list[Attachment])
async def my_attachments(
    db : AsyncSession = Depends(get_db),
    user: dict       = Depends(get_current_user),
):
    return await list_by_user(db, UUID(user["sub"]))

@router.get("/{attachment_id}", response_model=Attachment)
async def read_attachment(
    attachment_id: UUID,
    db : AsyncSession = Depends(get_db),
    user: dict       = Depends(get_current_user),
):
    obj = await get_attachment(db, attachment_id)
    if not obj or obj.user_id != UUID(user["sub"]):
        raise HTTPException(status_code=404, detail="Attachment not found")
    return obj