from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta, timezone
from app.core.config import get_settings
import logging

# パスワードのハッシュ化に使用するコンテキスト
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# アプリ設定の取得
settings = get_settings()
SECRET_KEY = settings.secret_key or "unsafe-default"  # 本番ではKeyVaultなどを利用
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

async def authenticate_user(db: AsyncSession, username: str, password: str) -> User | None:
    """
    ユーザー名とパスワードを用いてユーザーを認証します。
    """
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()
    if user and pwd_context.verify(password, user.hashed_password):
        return user
    return None

def create_access_token(data: dict, expires_delta: timedelta | None = None, secret_key: str = SECRET_KEY, algorithm: str = ALGORITHM) -> str:
    """
    JWTアクセストークンを生成します。
    - `exp`: 有効期限（UNIX時刻）
    - `iat`: 発行時刻（UNIX時刻）
    - `sub`: サブジェクト（ユーザーIDなど）
    """
    try:
        now = datetime.now(tz=timezone.utc)
        expire = now + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
        payload = {
            "iat": int(now.timestamp()),
            "exp": int(expire.timestamp()),
            **data
        }
        encoded_jwt = jwt.encode(payload, secret_key, algorithm=algorithm)
        return encoded_jwt
    except Exception as e:
        logging.exception("JWT生成に失敗しました")
        raise RuntimeError("アクセストークンの生成に失敗しました") from e

async def update_last_login(db: AsyncSession, user_id: int):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user:
        user.last_login_at = datetime.utcnow()
        await db.commit()