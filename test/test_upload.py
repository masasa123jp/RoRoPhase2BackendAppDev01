import pytest
from httpx import AsyncClient
from io import BytesIO

@pytest.mark.asyncio
async def test_upload_valid_file(client: AsyncClient):
    file_content = BytesIO(b"Sample file content")
    files = {"file": ("test.txt", file_content, "text/plain")}
    response = await client.post("/upload/", files=files)
    assert response.status_code == 201
    data = response.json()
    assert "filename" in data
    assert data["content_type"] == "text/plain"

@pytest.mark.asyncio
async def test_upload_invalid_mime_type(client: AsyncClient):
    file_content = BytesIO(b"Sample file content")
    files = {"file": ("test.exe", file_content, "application/octet-stream")}
    response = await client.post("/upload/", files=files)
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid file type"

@pytest.mark.asyncio
async def test_upload_no_file(client: AsyncClient):
    response = await client.post("/upload/", files={})
    assert response.status_code == 422
    assert response.json()["detail"][0]["msg"] == "field required"
