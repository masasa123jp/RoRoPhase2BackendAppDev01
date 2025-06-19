# app/schemas/common.py

from pydantic import BaseModel, Field

class PasswordChangeRequest(BaseModel):
    """
    パスワード変更リクエスト用の入力バリデーションスキーマ。
    """
    old_password: str = Field(..., min_length=8, description="現在のパスワード")
    new_password: str = Field(..., min_length=8, description="新しいパスワード")
