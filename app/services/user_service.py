# app/services/user_service.py

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.schemas.user import UserCreate, UserRead
from passlib.context import CryptContext

# bcrypt によるパスワードハッシュ化設定
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def get_user_by_id(db: AsyncSession, user_id: int) -> UserRead | None:
    """
    指定したIDのアクティブユーザー（is_active=True）を取得。
    該当がなければ None を返す。
    """
    result = await db.execute(
        select(User).where(User.id == user_id, User.is_active == True)
    )
    user = result.scalar_one_or_none()
    return UserRead.from_orm(user) if user else None


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    """
    メールアドレスからユーザーを取得。
    アクティブ／非アクティブ問わず全件対象。
    """
    result = await db.execute(
        select(User).where(User.email == email)
    )
    return result.scalar_one_or_none()


async def get_all_users(db: AsyncSession, limit: int = 50, offset: int = 0) -> list[UserRead]:
    """
    アクティブユーザーの一覧をページネーション付きで取得。
    デフォルトで最大50件取得。
    """
    result = await db.execute(
        select(User)
        .where(User.is_active == True)
        .offset(offset)
        .limit(limit)
    )
    return [UserRead.from_orm(u) for u in result.scalars().all()]


async def get_inactive_users(db: AsyncSession) -> list[UserRead]:
    """
    非アクティブ（論理削除）ユーザーの一覧を取得。
    管理者画面などでの復元候補リストとして利用。
    """
    result = await db.execute(
        select(User).where(User.is_active == False)
    )
    return [UserRead.from_orm(u) for u in result.scalars().all()]


async def create_user(db: AsyncSession, user: UserCreate) -> UserRead:
    """
    新規ユーザーを作成。
    ・パスワードはbcryptでハッシュ化。
    ・作成後はDBからUserReadに変換して返却。
    """
    hashed = pwd_context.hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed,
        is_active=True
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return UserRead.from_orm(db_user)


async def update_user(db: AsyncSession, user_id: int, data: UserCreate) -> UserRead | None:
    """
    指定されたアクティブユーザーの情報を更新。
    ・存在しなければ None。
    ・パスワードは新規入力値で上書きハッシュ保存。
    """
    result = await db.execute(
        select(User).where(User.id == user_id, User.is_active == True)
    )
    db_user = result.scalar_one_or_none()
    if not db_user:
        return None

    db_user.username = data.username
    db_user.email = data.email
    db_user.hashed_password = pwd_context.hash(data.password)

    await db.commit()
    await db.refresh(db_user)
    return UserRead.from_orm(db_user)


async def deactivate_user(db: AsyncSession, user_id: int) -> bool:
    """
    アクティブユーザーを論理削除（is_active=False）に設定。
    ・該当しない場合は False。
    """
    result = await db.execute(
        select(User).where(User.id == user_id, User.is_active == True)
    )
    db_user = result.scalar_one_or_none()
    if not db_user:
        return False

    db_user.is_active = False
    await db.commit()
    return True


async def restore_user(db: AsyncSession, user_id: int) -> bool:
    """
    非アクティブユーザーを復元（is_active=True）。
    ・該当しない場合は False。
    """
    result = await db.execute(
        select(User).where(User.id == user_id, User.is_active == False)
    )
    db_user = result.scalar_one_or_none()
    if not db_user:
        return False

    db_user.is_active = True
    await db.commit()
    return True


async def change_password(db: AsyncSession, user_id: int, old_password: str, new_password: str) -> bool:
    """
    認証済みユーザーが自身のパスワードを変更。
    ・旧パスワードが一致しない場合は False。
    """
    result = await db.execute(
        select(User).where(User.id == user_id, User.is_active == True)
    )
    db_user = result.scalar_one_or_none()
    if not db_user:
        return False

    if not pwd_context.verify(old_password, db_user.hashed_password):
        return False

    db_user.hashed_password = pwd_context.hash(new_password)
    await db.commit()
    return True


async def force_reset_password(db: AsyncSession, user_id: int, new_password: str) -> bool:
    """
    管理者による任意ユーザーのパスワード強制リセット処理。
    ・旧パスワードの照合なし。
    ・対象が存在しない場合は False。
    """
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    db_user = result.scalar_one_or_none()
    if not db_user:
        return False

    db_user.hashed_password = pwd_context.hash(new_password)
    await db.commit()
    return True

from sqlalchemy import or_

async def search_users_by_criteria(
    db: AsyncSession,
    query: str,
    is_active: bool | None = None,
    limit: int = 50,
    offset: int = 0
) -> list[UserRead]:
    stmt = select(User).where(
        or_(
            User.username.ilike(f"%{query}%"),
            User.email.ilike(f"%{query}%")
        )
    )

    if is_active is not None:
        stmt = stmt.where(User.is_active == is_active)

    stmt = stmt.offset(offset).limit(limit)
    result = await db.execute(stmt)
    return [UserRead.from_orm(u) for u in result.scalars().all()]