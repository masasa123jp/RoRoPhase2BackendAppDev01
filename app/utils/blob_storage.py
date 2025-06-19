from azure.storage.blob.aio import BlobServiceClient
from app.core.config import get_settings

settings = get_settings()
blob_service_client = BlobServiceClient.from_connection_string(settings.storage_conn)

async def upload_file(container_name: str, blob_name: str, data: bytes) -> str:
    container_client = blob_service_client.get_container_client(container_name)
    await container_client.upload_blob(name=blob_name, data=data)
    return f"https://{blob_service_client.account_name}.blob.core.windows.net/{container_name}/{blob_name}"
