from pydantic import BaseModel, EmailStr
from typing import Optional
from uuid import UUID

class ReportRequest(BaseModel):
    pet_id: UUID
    pet_name: str
    species: str
    breed: str
    age: str
    email: Optional[EmailStr] = None
    use_openai: bool = False  # OpenAI連携の有無を指定

class ReportResponse(BaseModel):
    report_id: str
    status: str
    download_url: Optional[str] = None
