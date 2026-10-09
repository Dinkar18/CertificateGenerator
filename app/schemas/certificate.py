from pydantic import BaseModel, ConfigDict
from datetime import datetime
from app.core.constants import CertificateStatus

class CertificateResponse(BaseModel):
    id: str
    job_id: str
    recipient_name: str
    recipient_email: str | None = None
    status: CertificateStatus
    file_path: str | None = None
    error_message: str | None = None
    created_at: datetime
    completed_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
