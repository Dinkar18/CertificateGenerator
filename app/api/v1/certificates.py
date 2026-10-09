import os
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import logging

from app.db.database import get_db
from app.schemas.certificate import CertificateResponse
from app.services.certificate_service import get_certificate
from app.core.constants import CertificateStatus
from app.core.errors import ErrorCodes, ErrorMessages, get_error_detail

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/{certificate_id}")
def get_certificate_endpoint(certificate_id: str, db: Session = Depends(get_db)):
    cert = get_certificate(db, certificate_id)
    if not cert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=get_error_detail(ErrorCodes.CERTIFICATE_NOT_FOUND, ErrorMessages.CERTIFICATE_NOT_FOUND)
        )
        
    if cert.status == CertificateStatus.SUCCESS:
        if cert.file_path and os.path.exists(cert.file_path):
            return FileResponse(cert.file_path, media_type='application/pdf', filename=f"{cert.recipient_name}_certificate.pdf")
        else:
            logger.error(f"Certificate file missing: {cert.file_path}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=get_error_detail(ErrorCodes.FILE_MISSING, ErrorMessages.FILE_MISSING)
            )
            
    elif cert.status == CertificateStatus.FAILED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=get_error_detail(ErrorCodes.CERTIFICATE_FAILED, ErrorMessages.certificate_failed(cert.error_message))
        )
        
    else:
        # PENDING or PROCESSING
        raise HTTPException(
            status_code=status.HTTP_202_ACCEPTED,
            detail=get_error_detail(ErrorCodes.CERTIFICATE_PROCESSING, ErrorMessages.CERTIFICATE_PROCESSING)
        )

@router.get("/{certificate_id}/status", response_model=CertificateResponse)
def get_certificate_status_endpoint(certificate_id: str, db: Session = Depends(get_db)):
    cert = get_certificate(db, certificate_id)
    if not cert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=get_error_detail(ErrorCodes.CERTIFICATE_NOT_FOUND, ErrorMessages.CERTIFICATE_NOT_FOUND)
        )
    return cert
