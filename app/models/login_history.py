# ---------- モデル ----------
import uuid, ipaddress
from datetime import datetime
from sqlalchemy import Column, DateTime, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, INET
from sqlalchemy.orm import relationship
from app.core.database import Base

class LoginHistory(Base):
    id         = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id    = Column(UUID(as_uuid=True), ForeignKey("user.id"))
    ip_address = Column(INET, nullable=False)
    user_agent = Column(String(300))
    logged_at  = Column(DateTime, default=datetime.now)

    user = relationship("User", back_populates="login_histories")
