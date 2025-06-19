import os
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.file import File
from datetime import datetime
from uuid import uuid4

UPLOAD_DIRECTORY = "uploads"

async def save_file_metadata(db: AsyncSession, file: UploadFile, user_id: int) -> str:
    """
    アップロードされたファイルのメタデータを保存し、ファイルを保存します。
    """
    # ファイル名の生成
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid4().hex}{file_extension}"
    file_path = os.path.join(UPLOAD_DIRECTORY, unique_filename)

    # ディレクトリが存在しない場合は作成
    os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)

    # ファイルの保存
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)

    # メタデータの保存
    db_file = File(
        filename=file.filename,
        filepath=file_path,
        content_type=file.content_type,
        uploaded_at=datetime.utcnow(),
        user_id=user_id
    )
    db.add(db_file)
    await db.commit()
    await db.refresh(db_file)

    return file_path
