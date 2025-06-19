from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
import logging

# ロガーの設定
logger = logging.getLogger("uvicorn.error")

class ExceptionHandlerMiddleware(BaseHTTPMiddleware):
    """
    すべてのリクエストに対して例外をキャッチし、統一されたエラーレスポンスを返すミドルウェア。
    """

    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except Exception as exc:
            logger.error(f"Unhandled exception: {exc}")
            return JSONResponse(
                status_code=500,
                content={"detail": "Internal Server Error"},
            )
