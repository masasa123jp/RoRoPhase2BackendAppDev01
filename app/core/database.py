from __future__ import annotations

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase, declared_attr
from sqlalchemy import MetaData

from app.core.config import get_settings

settings = get_settings()

# 命名規約の定義
NAMING_CONVENTION: dict[str, str] = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "pk": "pk_%(table_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
}

# メタデータオブジェクトの作成
metadata_obj = MetaData(naming_convention=NAMING_CONVENTION)

# 共通の基底クラスの定義
class Base(DeclarativeBase):
    """全モデルが継承する基底クラス"""
    metadata = metadata_obj

    # __tablename__ を自動生成 (CamelCase → snake_case)
    @declared_attr.directive
    def __tablename__(cls) -> str:  # type: ignore
        name = cls.__name__
        # シンプルに lower, ただし連続大文字 (UUID 等) は分割しない
        snake = []
        for i, c in enumerate(name):
            if c.isupper() and i != 0 and not name[i - 1].isupper():
                snake.append("_")
            snake.append(c.lower())
        return "".join(snake)

# データベース接続URLを設定
DATABASE_URL = settings.DATABASE_URL

# 非同期エンジンの作成
engine = create_async_engine(
    DATABASE_URL,
    echo=False,  # SQLAlchemyのログ出力を無効化（必要に応じてTrueに設定）
    future=True,  # SQLAlchemy 2.0スタイルの使用を有効化
)

# 非同期セッションメーカーの作成
async_session = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,  # コミット後にオブジェクトの属性を期限切れにしない
    class_=AsyncSession,
)

# データベースセッションを取得するための依存関数
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    非同期データベースセッションを生成し、リクエストのライフサイクルに合わせて管理します。
    """
    async with async_session() as session:
        yield session



