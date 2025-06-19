from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from fastapi import status
from app.core.security import verify_token
import logging

# ロガーの設定
logger = logging.getLogger("uvicorn.error")

class AuthMiddleware(BaseHTTPMiddleware):
    """
    リクエストに含まれるトークンを検証し、認証を行うミドルウェア。
    """

    async def dispatch(self, request: Request, call_next):
        authorization: str = request.headers.get("Authorization")
        if authorization:
            scheme, _, token = authorization.partition(" ")
            if scheme.lower() != "bearer":
                return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content={"detail": "Invalid authentication scheme."})
            if not verify_token(token):
                return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content={"detail": "Invalid or expired token."})
        else:
            return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content={"detail": "Authorization header missing."})

        response = await call_next(request)
        return response
