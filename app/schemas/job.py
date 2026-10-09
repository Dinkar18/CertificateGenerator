from pydantic import BaseModel, ConfigDict, Field, EmailStr
from typing import List
from datetime import datetime
from app.core.constants import JobStatus

class RecipientCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr | None = None

class JobCreate(BaseModel):
    event_name: str = Field(..., min_length=1, max_length=255)
    event_date: str = Field(..., min_length=1, max_length=50)
    issuer_name: str = Field(..., min_length=1, max_length=255)
    recipients: List[RecipientCreate] = Field(..., min_length=1)

class CertificateBasicInfo(BaseModel):
    id: str
    recipient_name: str
    status: str
    error_message: str | None = None

    model_config = ConfigDict(from_attributes=True)

class JobResponse(BaseModel):
    id: str
    event_name: str
    event_date: str
    issuer_name: str
    status: JobStatus
    total: int = Field(alias="total_count")
    successful: int = Field(alias="success_count")
    failed: int = Field(alias="failure_count")
    progress_percentage: int
    created_at: datetime
    started_at: datetime | None = None
    completed_at: datetime | None = None
    certificates: List[CertificateBasicInfo] = []

    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

    @classmethod
    def from_orm(cls, obj):
        progress = 0 if obj.total_count == 0 else int(((obj.success_count + obj.failure_count) / obj.total_count) * 100)
            
        return cls(
            id=obj.id,
            event_name=obj.event_name,
            event_date=obj.event_date,
            issuer_name=obj.issuer_name,
            status=obj.status,
            total=obj.total_count,
            successful=obj.success_count,
            failed=obj.failure_count,
            progress_percentage=progress,
            created_at=obj.created_at,
            started_at=obj.started_at,
            completed_at=obj.completed_at,
            certificates=getattr(obj, "certificates", [])
        )
