from contextlib import asynccontextmanager
from typing import AsyncGenerator, Dict, Any
from fastapi import Header, HTTPException, status
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from ..core.config import get_settings
from ..core.security import verify_jwt

cfg = get_settings()
engine = create_async_engine(cfg.postgres_uri, pool_pre_ping=True, echo=False)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)

@asynccontextmanager
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session

async def get_current_user(authorization: str = Header(..., alias="Authorization")) -> Dict[str, Any]:
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise ValueError
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Bearer トークンが必要です")
    try:
        return verify_jwt(token)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc))
