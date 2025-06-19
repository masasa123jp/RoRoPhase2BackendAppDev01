"""
app/dependencies/user_auth.py

OIDC（OpenID Connect）トークンで認証し、
認証済みユーザー情報（Userモデル）をDBから取得する依存関数群。
複数IDプロバイダー（Azure AD B2C, Google, GitHubなど）対応。
"""

from fastapi import Depends, HTTPException, status, Header
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User, UserAuthProvider

# 必要に応じて設定ファイルやenvから共通パラメータをimport
from app.core.config import get_settings
settings = get_settings()

# プロバイダーごとに有効なissuer・public_keyなどは設定ファイル・envで管理推奨

async def get_current_user(
    authorization: str = Header(..., alias="Authorization"),
    db: AsyncSession = Depends(),  # FastAPIの依存でdbをDI
) -> User:
    """
    HTTP AuthorizationヘッダーからIDトークン（JWT）を取得し、ユーザーを認証・返却。
    - トークンの検証は事前にミドルウェア・またはこの関数内でJOSE/jwtにて実施。
    - 外部IDプロバイダーのsub/issを使ってuser_auth_providersテーブルと突合。
    """
    # "Bearer <token>" 形式のチェック
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Bearer token required")
    token = authorization.split(" ", 1)[1]

    # トークンのデコード・検証（ここでは署名検証を省略し構造のみ。実運用では公開鍵/issuer検証が必須）
    try:
        token_payload = jwt.get_unverified_claims(token)
        iss = token_payload.get("iss")
        sub = token_payload.get("sub")
        if not iss or not sub:
            raise ValueError
    except (JWTError, ValueError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid ID token")

    provider = extract_provider_from_iss(iss)
    provider_subject = sub

    # DBでプロバイダーとprovider_subjectでユーザー検索
    result = await db.execute(
        select(User)
        .join(UserAuthProvider)
        .where(
            UserAuthProvider.provider == provider,
            UserAuthProvider.provider_subject == provider_subject,
        )
    )
    user = result.scalar_one_or_none()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    return user

def extract_provider_from_iss(iss: str) -> str:
    """
    issuer(iss)の値を元に認証プロバイダー名を返す。
    必要に応じてパターンを追加。
    """
    if "login.microsoftonline.com" in iss:
        return "azure_b2c"
    if "accounts.google.com" in iss:
        return "google"
    if "github.com" in iss:
        return "github"
    # 追加プロバイダーにも柔軟に対応
    return "unknown"

# 例: APIルーターで利用
"""
from app.dependencies.user_auth import get_current_user

@router.get("/me", response_model=UserRead)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user
"""
