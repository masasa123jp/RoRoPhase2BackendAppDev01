# app/models/report_log.py

from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
from uuid import uuid4

from app.core.database import Base

class ReportLog(Base):
    """
    レポート生成履歴のログモデル。
    どのユーザーがどのペットに対していつレポートを生成したかを記録する。
    """
    __tablename__ = "report_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    pet_id  = Column(UUID(as_uuid=True), ForeignKey("pets.id"), nullable=False)

    summary = Column(Text, nullable=True)  # 要約（OpenAIの応答などを格納）
    pdf_path = Column(String, nullable=True)  # 生成されたPDFファイルのパス

    created_at = Column(DateTime, default=datetime.utcnow)

    # リレーション
    user = relationship("User") #← 必要に応じて
    pet = relationship("Pet")
