from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from app.core.database import Base

class Category(Base):
    __tablename__ = "categories"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)

    submissions = relationship("SurveySubmission", back_populates="category")
