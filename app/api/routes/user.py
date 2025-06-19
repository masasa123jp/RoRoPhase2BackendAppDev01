# app/api/routes/user.py

from fastapi import APIRouter, Depends, HTTPException, status, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.user import UserRead, UserCreate
from app.schemas.common import PasswordChangeRequest
from app.services.user_service import (
    get_user_by_id,
    get_all_users,
    get_inactive_users,
    get_user_by_email,
    create_user,
    update_user,
    deactivate_user,
    restore_user,
    change_password,
    force_reset_password,
    search_users_by_criteria
)
from app.events.event_handler import log_event
from app.core.database import get_db
from app.core.security import get_current_user, has_admin_role

router = APIRouter()

@router.get("/users/", response_model=list[UserRead], summary="全アクティブユーザー一覧（管理者）")
async def list_users(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    _: None = Depends(has_admin_role)
):
    """
    アクティブなユーザーをページネーション付きで一覧取得。
    ペット情報（petsリスト）も含まれる場合、スキーマ側で `UserRead` に統合されている想定。
    """
    return await get_all_users(db, limit=limit, offset=offset)

@router.get("/users/inactive", response_model=list[UserRead], summary="非アクティブユーザー一覧（管理者）")
async def list_inactive_users(
    db: AsyncSession = Depends(get_db),
    _: None = Depends(has_admin_role)
):
    """
    論理削除された（is_active=False）ユーザーを一覧取得。
    管理者のみがアクセス可能。
    """
    return await get_inactive_users(db)

@router.get("/users/me", response_model=UserRead)
async def read_current_user(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    現在ログインしているユーザー自身のプロフィールを取得。
    ユーザーが飼っているペット一覧（pets）も含まれる場合、UserReadで対応。
    """
    user = await get_user_by_id(db, current_user["id"])
    if not user:
        raise HTTPException(status_code=404, detail="ユーザーが見つかりません")
    return user

@router.get("/users/{user_id}", response_model=UserRead)
async def read_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(has_admin_role)
):
    """
    任意のユーザーIDのプロフィールを取得（管理者専用）。
    is_active=Trueのユーザーが対象。
    """
    user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="ユーザーが存在しません")
    return user

@router.post("/users/", response_model=UserRead)
async def create_new_user(
    user: UserCreate,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(has_admin_role)
):
    """
    管理者が新規ユーザーを作成する。
    メールアドレスが重複する場合は409エラーを返す。
    """
    existing = await get_user_by_email(db, user.email)
    if existing:
        raise HTTPException(status_code=409, detail="このメールアドレスは既に登録されています")
    return await create_user(db, user)

@router.put("/users/{user_id}", response_model=UserRead)
async def update_my_user(
    user_id: int,
    user_update: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    自分自身のユーザー情報を更新。
    他人の情報を更新しようとすると403エラー。
    """
    if user_id != current_user["id"]:
        raise HTTPException(status_code=403, detail="自身以外のユーザー情報は更新できません")
    updated = await update_user(db, user_id, user_update)
    if not updated:
        raise HTTPException(status_code=404, detail="ユーザーが存在しません")
    return updated

@router.delete("/users/{user_id}")
async def deactivate_user_route(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    _: None = Depends(has_admin_role)
):
    """
    ユーザーを論理削除する（is_active=False）。
    削除されたユーザーに紐づくペットも削除される（CASCADE設定）。
    操作ログはイベントとして記録。
    """
    success = await deactivate_user(db, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="対象ユーザーが見つかりません")
    log_event("user_deactivated", current_user["id"], {"target_user_id": user_id})
    return {"detail": "ユーザーを無効化しました"}

@router.put("/users/{user_id}/restore")
async def restore_user_route(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(has_admin_role)
):
    """
    論理削除されたユーザー（is_active=False）を復元（is_active=True）する。
    """
    success = await restore_user(db, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="対象ユーザーが見つかりません")
    return {"detail": "ユーザーを復元しました"}

@router.put("/users/me/password")
async def change_my_password(
    request: PasswordChangeRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    現在ログインしているユーザーが、自身のパスワードを変更する。
    古いパスワードが一致しない場合はエラー。
    """
    success = await change_password(db, current_user["id"], request.old_password, request.new_password)
    if not success:
        raise HTTPException(status_code=400, detail="現在のパスワードが一致しません")
    return {"detail": "パスワードを変更しました"}

@router.put("/users/{user_id}/reset-password")
async def reset_user_password(
    user_id: int,
    request: PasswordChangeRequest,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(has_admin_role)
):
    """
    管理者が任意のユーザーのパスワードを強制リセットする。
    """
    success = await force_reset_password(db, user_id, request.new_password)
    if not success:
        raise HTTPException(status_code=404, detail="ユーザーが存在しません")
    return {"detail": "パスワードをリセットしました"}

@router.get("/users/search", response_model=list[UserRead])
async def search_users(
    query: str = Query(""),
    is_active: bool | None = Query(None),
    limit: int = Query(50),
    offset: int = Query(0),
    db: AsyncSession = Depends(get_db),
    _: None = Depends(has_admin_role)
):
    """
    ユーザーを名前またはメールアドレスで部分一致検索。
    is_active によりアクティブ／非アクティブのフィルタも可能。
    ペット情報も含めて表示されるように、UserReadに組み込まれている想定。
    """
    users = await search_users_by_criteria(db, query=query, is_active=is_active, limit=limit, offset=offset)
    return users
