import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_login_success(client: AsyncClient):
    login_data = {"username": "testuser", "password": "securepassword"}
    response = await client.post("/auth/token", data=login_data)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

@pytest.mark.asyncio
async def test_login_invalid_credentials(client: AsyncClient):
    login_data = {"username": "testuser", "password": "wrongpassword"}
    response = await client.post("/auth/token", data=login_data)
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username or password"

@pytest.mark.asyncio
async def test_access_protected_route_without_token(client: AsyncClient):
    response = await client.get("/protected-route/")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"
