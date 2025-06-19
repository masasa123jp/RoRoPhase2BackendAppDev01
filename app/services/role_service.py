from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.roles import Role
from app.models.user import User
from app.schemas.roles import RoleCreate, RoleRead

async def get_roles(db: AsyncSession) -> list[RoleRead]:
    """
    すべてのロールを取得します。
    """
    result = await db.execute(select(Role))
    roles = result.scalars().all()
    return [RoleRead.from_orm(role) for role in roles]

async def create_role(db: AsyncSession, role: RoleCreate) -> RoleRead:
    """
    新しいロールを作成します。
    """
    db_role = Role(name=role.name)
    db.add(db_role)
    await db.commit()
    await db.refresh(db_role)
    return RoleRead.from_orm(db_role)

async def assign_role(db: AsyncSession, user_id: int, role_id: int) -> None:
    """
    指定されたユーザーにロールを割り当てます。
    """
    user_result = await db.execute(select(User).where(User.id == user_id))
    user = user_result.scalar_one_or_none()
    role_result = await db.execute(select(Role).where(Role.id == role_id))
    role = role_result.scalar_one_or_none()
    if user and role:
        user.roles.append(role)
        await db.commit()
