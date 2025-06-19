from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class Question(Base):
    __tablename__ = "questions"

    id = Column(String, primary_key=True, index=True)
    text = Column(String, nullable=False)
    category_id = Column(String, ForeignKey("categories.id"), nullable=False)

    category = relationship("Category", back_populates="questions")
    choices = relationship("Choice", back_populates="question")
