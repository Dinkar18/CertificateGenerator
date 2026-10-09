import logging
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.models.generation_job import GenerationJob
from app.models.certificate import Certificate
from app.core.constants import JobStatus, CertificateStatus
from app.services.certificate_generator import CertificateGenerator

logger = logging.getLogger(__name__)

def process_generation_job(job_id: str):
    logger.info(f"Background worker started for job_id={job_id}")
    db: Session = SessionLocal()
    
    try:
        # Fetch the job
        job = db.query(GenerationJob).filter(GenerationJob.id == job_id).first()
        if not job:
            logger.error(f"Job {job_id} not found.")
            return
            
        job.status = JobStatus.PROCESSING
        job.started_at = datetime.now(timezone.utc)
        db.commit()
        
        generator = CertificateGenerator()
        
        certificates = db.query(Certificate).filter(Certificate.job_id == job_id).all()
        
        for cert in certificates:
            if cert.status in (CertificateStatus.SUCCESS, CertificateStatus.FAILED):
                continue  # Idempotency: skip already processed
                
            try:
                cert.status = CertificateStatus.PROCESSING
                db.commit()
                
                cert.file_path = generator.generate(
                    job_id=job.id,
                    certificate_id=cert.id,
                    recipient_name=cert.recipient_name,
                    event_name=job.event_name,
                    event_date=job.event_date,
                    issuer_name=job.issuer_name
                )
                cert.status = CertificateStatus.SUCCESS
                logger.info(f"CERTIFICATE_GENERATION_SUCCESS: cert_id={cert.id}")
                
            except Exception as e:
                logger.error(f"CERTIFICATE_GENERATION_FAILED: cert_id={cert.id} error={e}")
                cert.status = CertificateStatus.FAILED
                cert.error_message = str(e)
                
            cert.completed_at = datetime.now(timezone.utc)
            db.commit()
            
        # Update job final status by querying current certificate states
        job.success_count = sum(1 for c in certificates if c.status == CertificateStatus.SUCCESS)
        job.failure_count = sum(1 for c in certificates if c.status == CertificateStatus.FAILED)
        job.completed_at = datetime.now(timezone.utc)
        
        job.status = JobStatus.COMPLETED if job.failure_count == 0 else JobStatus.COMPLETED_WITH_ERRORS
        logger.info(f"JOB_FINISHED: job_id={job_id} status={job.status}")
        db.commit()
        
    except Exception as e:
        logger.exception(f"Unexpected error in background worker for job_id={job_id}: {e}")
    finally:
        db.close()
