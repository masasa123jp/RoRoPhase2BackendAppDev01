import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from backend.shared_lib.db import AsyncSessionLocal
from backend.app.models import Base, User, Category
from backend.app.core.config import get_settings

settings = get_settings()

async def seed():
    async with AsyncSessionLocal() as session:
        # ユーザーの作成
        user = User(
            id="user_1",
            email="admin@example.com",
            hashed_password="hashed_password",
            is_active=True
        )
        session.add(user)

        # カテゴリの作成
        category = Category(
            id="cat_1",
            name="General"
        )
        session.add(category)

        await session.commit()

if __name__ == "__main__":
    asyncio.run(seed())
