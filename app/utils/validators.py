from fastapi import UploadFile, HTTPException
import imghdr
import os

async def validate_upload_file(file: UploadFile, allowed_extensions: list, allowed_mime_types: list):
    """
    アップロードされたファイルの拡張子と MIME タイプを検証します。
    """
    filename = file.filename
    content_type = file.content_type

    # ファイル拡張子の検証
    ext = os.path.splitext(filename)[1].lower()
    if ext not in allowed_extensions:
        raise HTTPException(status_code=400, detail="Unsupported file extension.")

    # MIME タイプの検証
    if content_type not in allowed_mime_types:
        raise HTTPException(status_code=400, detail="Unsupported file type.")

    # 追加の検証（例: 画像ファイルの実際の形式を確認）
    if 'image' in content_type:
        contents = await file.read()
        file_type = imghdr.what(None, h=contents)
        if file_type not in [ext.strip('.') for ext in allowed_extensions]:
            raise HTTPException(status_code=400, detail="Invalid image file.")
        await file.seek(0)  # ファイルポインタを先頭に戻す
from fastapi import UploadFile, HTTPException
import imghdr
import os

async def validate_upload_file(file: UploadFile, allowed_extensions: list, allowed_mime_types: list):
    """
    アップロードされたファイルの拡張子と MIME タイプを検証します。
    """
    filename = file.filename
    content_type = file.content_type

    # ファイル拡張子の検証
    ext = os.path.splitext(filename)[1].lower()
    if ext not in allowed_extensions:
        raise HTTPException(status_code=400, detail="Unsupported file extension.")

    # MIME タイプの検証
    if content_type not in allowed_mime_types:
        raise HTTPException(status_code=400, detail="Unsupported file type.")

    # 追加の検証（例: 画像ファイルの実際の形式を確認）
    if 'image' in content_type:
        contents = await file.read()
        file_type = imghdr.what(None, h=contents)
        if file_type not in [ext.strip('.') for ext in allowed_extensions]:
            raise HTTPException(status_code=400, detail="Invalid image file.")
        await file.seek(0)  # ファイルポインタを先頭に戻す
