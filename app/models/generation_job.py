import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, DateTime, Enum as SAEnum
from sqlalchemy.orm import relationship
from app.db.database import Base
from app.core.constants import JobStatus

class GenerationJob(Base):
    __tablename__ = "generation_jobs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    event_name = Column(String(255), nullable=False)
    event_date = Column(String(50), nullable=False)
    issuer_name = Column(String(255), nullable=False)
    status = Column(SAEnum(JobStatus), default=JobStatus.PENDING, nullable=False)
    
    total_count = Column(Integer, default=0, nullable=False)
    success_count = Column(Integer, default=0, nullable=False)
    failure_count = Column(Integer, default=0, nullable=False)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    certificates = relationship("Certificate", back_populates="job", cascade="all, delete-orphan")
