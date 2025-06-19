# ---------- CRUD ----------
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import select
from app.models.login_history import LoginHistory

async def record_login(db: AsyncSession, *, user_id: UUID, ip: str, ua: str | None):
    obj = LoginHistory(user_id=user_id, ip_address=ip, user_agent=ua)
    db.add(obj)
    await db.commit()

async def list_logins(db: AsyncSession, user_id: UUID):
    res = await db.scalars(
        select(LoginHistory).where(LoginHistory.user_id == user_id).order_by(LoginHistory.logged_at.desc())
    )
    return list(res)
