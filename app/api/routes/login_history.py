# ---------- ルーター ----------
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from ..dependencies import get_db, get_current_user
from ...schemas.login_history import LoginHistoryOut
from ...crud.login_history import list_logins

router = APIRouter(prefix="/login_history", tags=["LoginHistory"])

@router.get("/", response_model=list[LoginHistoryOut])
async def my_logins(
    db : AsyncSession = Depends(get_db),
    user: dict       = Depends(get_current_user),
):
    return await list_logins(db, UUID(user["sub"]))
