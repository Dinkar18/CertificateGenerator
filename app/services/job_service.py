from sqlalchemy.orm import Session
from app.models.generation_job import GenerationJob
from app.models.certificate import Certificate
from app.schemas.job import JobCreate
from app.core.constants import JobStatus

def create_generation_job(db: Session, job_data: JobCreate) -> GenerationJob:
    total_count = len(job_data.recipients)
    
    db_job = GenerationJob(
        event_name=job_data.event_name,
        event_date=job_data.event_date,
        issuer_name=job_data.issuer_name,
        total_count=total_count,
        status=JobStatus.PENDING
    )
    db.add(db_job)
    db.flush() # flush to get job ID
    
    db_certificates = []
    for recipient in job_data.recipients:
        cert = Certificate(
            job_id=db_job.id,
            recipient_name=recipient.name,
            recipient_email=recipient.email
        )
        db_certificates.append(cert)
        
    db.add_all(db_certificates)
    db.commit()
    db.refresh(db_job)
    
    return db_job

def get_job(db: Session, job_id: str) -> GenerationJob:
    return db.query(GenerationJob).filter(GenerationJob.id == job_id).first()
