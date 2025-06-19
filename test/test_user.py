import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.user import UserCreate

@pytest.mark.asyncio
async def test_create_user(client: AsyncClient, db_session: AsyncSession):
    user_data = {"username": "testuser", "email": "test@example.com", "password": "securepassword"}
    response = await client.post("/users/", json=user_data)
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == user_data["username"]
    assert data["email"] == user_data["email"]

@pytest.mark.asyncio
async def test_create_user_existing_email(client: AsyncClient, db_session: AsyncSession):
    user_data = {"username": "testuser2", "email": "test@example.com", "password": "securepassword"}
    response = await client.post("/users/", json=user_data)
    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"

@pytest.mark.asyncio
async def test_get_user_unauthorized(client: AsyncClient):
    response = await client.get("/users/me")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"
