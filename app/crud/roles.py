# ---------- CRUD ----------
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import select
from app.models.roles import Role, user_role_link
from app.schemas.roles import RoleCreate

async def create_role(db: AsyncSession, data: RoleCreate):
    obj = Role(**data.dict())
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj

async def assign_role(db: AsyncSession, user_id: UUID, role_id: UUID):
    sql = user_role_link.insert().values(user_id=user_id, role_id=role_id).prefix_with("ON CONFLICT DO NOTHING")
    await db.execute(sql)
    await db.commit()

async def list_roles(db: AsyncSession):
    rows = await db.scalars(select(Role))
    return list(rows)
