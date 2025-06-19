# app/api/routes/auth.py

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.auth_service import authenticate_user, create_access_token, update_last_login
from app.core.security import SECRET_KEY, ALGORITHM

import logging

# ルーターの作成
router = APIRouter()

@router.post(
    "/token",
    summary="トークン発行（ログイン）",
    response_description="JWTアクセストークンを返します"
)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """
    ユーザー認証およびJWTトークンの発行を行うエンドポイント。

    - 認証失敗時は401エラーを返却。
    - 認証成功後、最終ログイン時刻（last_login_at）を更新。
    - JWTトークンを発行し、アクセストークンを返却。
    """
    try:
        # 認証処理（ユーザー名とパスワードを検証）
        user = await authenticate_user(db, form_data.username, form_data.password)
        if not user:
            logging.warning(f"認証失敗: username={form_data.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="ユーザー名またはパスワードが正しくありません。",
                headers={"WWW-Authenticate": "Bearer"}
            )

        # ✅ 最終ログイン日時を更新
        await update_last_login(db, user.id)

        # JWTアクセストークンの生成
        access_token = create_access_token(
            data={"sub": str(user.id), "is_admin": user.is_admin},
            secret_key=SECRET_KEY,
            algorithm=ALGORITHM
        )

        # アクセストークンを返却
        return {
            "access_token": access_token,
            "token_type": "bearer"
        }

    except Exception as e:
        # トークン生成またはその他処理中の例外を捕捉
        logging.error(f"トークン発行中にエラーが発生: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="認証処理中にエラーが発生しました"
        )
