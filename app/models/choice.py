from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class Choice(Base):
    __tablename__ = "choices"

    id = Column(String, primary_key=True, index=True)
    text = Column(String, nullable=False)
    question_id = Column(String, ForeignKey("questions.id"), nullable=False)

    question = relationship("Question", back_populates="choices")
