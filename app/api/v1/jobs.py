from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from sqlalchemy.orm import Session
import logging
import os
from app.db.database import get_db
from app.schemas.job import JobCreate, JobResponse
from app.services.job_service import create_generation_job, get_job
from app.workers.certificate_worker import process_generation_job
from app.core.config import settings
from app.core.errors import ErrorCodes, ErrorMessages, get_error_detail

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
def create_job(job_data: JobCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    if len(job_data.recipients) > settings.MAX_RECIPIENTS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=get_error_detail(ErrorCodes.TOO_MANY_RECIPIENTS, ErrorMessages.TOO_MANY_RECIPIENTS)
        )
        
    try:
        job = create_generation_job(db, job_data)
        logger.info(f"JOB_CREATED: job_id={job.id}")
        
        background_tasks.add_task(process_generation_job, job.id)
        logger.info(f"JOB_PROCESSING_STARTED: job_id={job.id}")
        
        return JobResponse.from_orm(job)
    except Exception as e:
        logger.error(f"Failed to create job: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=get_error_detail(ErrorCodes.INTERNAL_ERROR, ErrorMessages.INTERNAL_ERROR)
        )

@router.get("/{job_id}", response_model=JobResponse)
def get_job_status(job_id: str, db: Session = Depends(get_db)):
    job = get_job(db, job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=get_error_detail(ErrorCodes.JOB_NOT_FOUND, ErrorMessages.JOB_NOT_FOUND)
        )
    return JobResponse.from_orm(job)

@router.get("/{job_id}/download-zip")
def download_job_zip(job_id: str, db: Session = Depends(get_db)):
    job = get_job(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
        
    job_dir = os.path.join(settings.OUTPUT_DIRECTORY, job_id)
    if not os.path.exists(job_dir):
        raise HTTPException(status_code=404, detail="Certificates not generated yet")
        
    zip_path = os.path.join(settings.OUTPUT_DIRECTORY, f"{job_id}.zip")
    if not os.path.exists(zip_path):
        import shutil
        shutil.make_archive(os.path.join(settings.OUTPUT_DIRECTORY, job_id), 'zip', job_dir)
        
    from fastapi.responses import FileResponse
    return FileResponse(
        zip_path, 
        media_type="application/zip", 
        filename=f"{job.event_name.replace(' ', '_')}_Certificates.zip"
    )
