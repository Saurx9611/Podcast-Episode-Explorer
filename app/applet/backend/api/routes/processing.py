from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from backend.api.dependencies import get_db
from backend.schemas.processing_schemas import ProcessingJobResponse
from backend.models import ProcessingJob, Episode

router = APIRouter(prefix="/processing", tags=["processing"])

@router.get("/jobs", response_model=List[ProcessingJobResponse])
def get_jobs(db: Session = Depends(get_db)):
    jobs = db.query(ProcessingJob).order_by(ProcessingJob.started_at.desc()).all()
    # Add episode_title for convenience
    for job in jobs:
        if job.episode:
            job.episode_title = job.episode.title
    return jobs

@router.get("/episodes/{episode_id}/jobs", response_model=List[ProcessingJobResponse])
def get_episode_jobs(episode_id: str, db: Session = Depends(get_db)):
    jobs = db.query(ProcessingJob).filter(ProcessingJob.episode_id == episode_id).order_by(ProcessingJob.started_at.desc()).all()
    return jobs
