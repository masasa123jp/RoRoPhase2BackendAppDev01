from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging

# ロガーの設定
logger = logging.getLogger("uvicorn.error")

async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """
    HTTPException のカスタムハンドラー。
    エラー詳細をログに記録し、クライアントに JSON レスポンスを返します。
    """
    logger.warning(f"HTTP error occurred: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    バリデーションエラーのカスタムハンドラー。
    エラー詳細をログに記録し、クライアントに JSON レスポンスを返します。
    """
    logger.warning(f"Validation error: {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()},
    )

async def generic_exception_handler(request: Request, exc: Exception):
    """
    その他の予期しない例外のカスタムハンドラー。
    エラー詳細をログに記録し、クライアントに汎用的なエラーメッセージを返します。
    """
    logger.error(f"Unexpected error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error"},
    )
