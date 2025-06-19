from typing import Annotated
from pydantic import BaseModel, EmailStr, StringConstraints

# ユーザー名の制約: 最小3文字、最大50文字
UsernameStr = Annotated[str, StringConstraints(min_length=3, max_length=50)]

# パスワードの制約: 最小8文字
PasswordStr = Annotated[str, StringConstraints(min_length=8)]

class UserBase(BaseModel):
    """
    ユーザーの共通属性を定義します。
    """
    username: UsernameStr  # ユーザー名の長さ制限
    email: EmailStr        # メールアドレスの形式を検証

class UserCreate(UserBase):
    """
    ユーザー作成時のスキーマを定義します。
    """
    password: PasswordStr  # パスワードの最小長を指定

class UserRead(UserBase):
    """
    ユーザー情報の読み取り用スキーマを定義します。
    """
    id: int                # ユーザーID
    is_active: bool        # アクティブ状態

    class Config:
        orm_mode = True    # ORMオブジェクトとの互換性を有効化



