# ---------- モデル ----------
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base

class Feedback(Base):
    id        = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id   = Column(UUID(as_uuid=True), ForeignKey("user.id"))
    category  = Column(String(80))     # 例: bug / feature / other
    message   = Column(Text, nullable=False)
    handled   = Column(String(10), default="pending")  # pending/closed
    created_at= Column(DateTime, default=datetime.now)

    user = relationship("User", back_populates="feedbacks")
