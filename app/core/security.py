# app/core/security.py

from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from typing import Optional, List, Callable
import os
import logging

# パスワードハッシュ設定（bcryptを使用）
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT設定（.envやKeyVaultでSECRET_KEYを管理することを推奨）
SECRET_KEY = os.getenv("SECRET_KEY", "your_secret_key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# OAuth2のスキーム設定（トークン発行エンドポイントを指定）
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# ------------------------------------------
# Pydanticを用いたアプリ内ユーザーモデル
# JWTに含まれるデータを表現
# ------------------------------------------
class TokenUser(BaseModel):
    id: str                  # JWTのsubに該当（UUID文字列）
    is_admin: bool = False   # 管理者フラグ


# ------------------------------------------
# パスワードのハッシュ化
# ------------------------------------------
def get_password_hash(password: str) -> str:
    """
    プレーンなパスワードをハッシュ化（bcrypt）して返す。
    """
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    平文パスワードとハッシュ値を照合する。
    """
    return pwd_context.verify(plain_password, hashed_password)

# ------------------------------------------
# アクセストークン（JWT）の生成
# ------------------------------------------
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None,
                        secret_key: str = SECRET_KEY, algorithm: str = ALGORITHM) -> str:
    """
    JWTトークンを生成する。
    - sub（ユーザーID）と is_admin（ロール）を含める
    - exp（有効期限）と iat（発行時刻）も含む
    """
    to_encode = data.copy()
    now = datetime.utcnow()
    expire = now + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))

    to_encode.update({
        "iat": now,
        "exp": expire
    })

    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=algorithm)
    return encoded_jwt

# ------------------------------------------
# 現在のユーザー情報をJWTから抽出して返す
# ------------------------------------------
async def get_current_user(token: str = Depends(oauth2_scheme)) -> TokenUser:
    """
    Authorizationヘッダーに含まれるBearerトークンを検証し、
    ユーザー情報（IDとロール）を返却する。
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="認証トークンが不正です。",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        is_admin: bool = payload.get("is_admin", False)

        if user_id is None:
            raise credentials_exception

        return TokenUser(id=user_id, is_admin=is_admin)

    except JWTError as e:
        logging.warning(f"JWTデコード失敗: {e}")
        raise credentials_exception

# ------------------------------------------
# 管理者ロール限定のアクセス制御（RBAC）
# ------------------------------------------
def has_admin_role(current_user: TokenUser = Depends(get_current_user)) -> None:
    """
    管理者（is_admin=True）のみアクセスを許可する。
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="この操作を行う権限がありません（管理者専用）"
        )
