import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import relationship
from app.db.database import Base
from app.core.constants import CertificateStatus

class Certificate(Base):
    __tablename__ = "certificates"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    job_id = Column(String(36), ForeignKey("generation_jobs.id"), nullable=False, index=True)
    
    recipient_name = Column(String(255), nullable=False)
    recipient_email = Column(String(255), nullable=True)
    
    status = Column(SAEnum(CertificateStatus), default=CertificateStatus.PENDING, nullable=False)
    file_path = Column(String(1024), nullable=True)
    error_message = Column(String(1024), nullable=True)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    completed_at = Column(DateTime, nullable=True)

    job = relationship("GenerationJob", back_populates="certificates")
