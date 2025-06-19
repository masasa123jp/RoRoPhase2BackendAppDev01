import asyncio
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.core.config import settings
from app.core.database import Base, get_db

# テスト用の非同期エンジンとセッションを作成
DATABASE_URL = settings.postgres_uri
engine_test = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionTest = sessionmaker(bind=engine_test, class_=AsyncSession, expire_on_commit=False)

# データベースの初期化とテーブル作成
@pytest.fixture(scope="session", autouse=True)
async def setup_database():
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine_test.dispose()

# テスト用のデータベースセッションを提供
@pytest.fixture
async def db_session():
    async with AsyncSessionTest() as session:
        yield session

# FastAPIの依存性をオーバーライドしてテスト用のセッションを使用
@pytest.fixture
async def client(db_session):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()
