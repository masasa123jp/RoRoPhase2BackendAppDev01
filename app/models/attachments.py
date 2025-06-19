# ========= モデル層 =========
# app/models/attachments.py
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base

class Attachment(Base):
    """Blob Storage 上のファイルに紐づくメタデータ"""
    id          = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id     = Column(UUID(as_uuid=True), ForeignKey("user.id", ondelete="CASCADE"))
    filename    = Column(String(255), nullable=False)
    blob_path   = Column(String(500), nullable=False, unique=True)
    mime_type   = Column(String(80),  nullable=False)
    size_bytes  = Column(String(40),  nullable=False)
    created_at  = Column(DateTime, default=datetime.now)

    user = relationship("User", back_populates="attachments")
