from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.roles import RoleCreate, RoleRead
from app.services.role_service import get_roles, create_role, assign_role
from app.core.database import get_db
from app.core.security import has_admin_role

router = APIRouter()

@router.get(
    "/roles/",
    response_model=list[RoleRead],
    summary="全ロール一覧取得（管理者のみ）"
)
async def list_roles(
    db: AsyncSession = Depends(get_db),
    _: None = Depends(has_admin_role)
):
    """
    管理者のみ全ロール一覧を取得可能。
    """
    return await get_roles(db)

@router.post(
    "/roles/",
    response_model=RoleRead,
    summary="新規ロール作成（管理者のみ）"
)
async def create_new_role(
    role: RoleCreate,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(has_admin_role)
):
    """
    管理者のみロール作成が可能。
    """
    return await create_role(db, role)

@router.post(
    "/roles/{role_id}/assign/{user_id}",
    summary="ユーザーへのロール付与（管理者のみ）"
)
async def assign_user_role(
    role_id: int,
    user_id: int,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(has_admin_role)
):
    """
    管理者のみユーザーへのロール割当が可能。
    """
    try:
        await assign_role(db, user_id, role_id)
    except Exception:
        raise HTTPException(status_code=400, detail="ロール付与に失敗しました")
    return {"detail": "ロールを割り当てました"}
