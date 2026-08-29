from typing import List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from backend.api.dependencies import get_processing_repo, get_episode_repo
from backend.repositories.processing_repo import ProcessingRepository
from backend.repositories.episode_repo import EpisodeRepository
from backend.schemas.processing_schemas import ProcessingJobResponse
from backend.models.processing_job import ProcessingJob
from backend.workers import pipeline_processor
from backend.core.exceptions import NotFoundException

router = APIRouter(prefix="/processing", tags=["processing"])

def format_time_ago(dt: datetime) -> str:
    if not dt:
        return "Unknown"
    now = datetime.now(timezone.utc)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    diff = now - dt
    seconds = int(diff.total_seconds())
    if seconds < 60:
        return "Just now"
    minutes = seconds // 60
    if minutes < 60:
        return f"{minutes} min{'s' if minutes > 1 else ''} ago"
    hours = minutes // 60
    if hours < 24:
        return f"{hours} hour{'s' if hours > 1 else ''} ago"
    days = hours // 24
    return f"{days} day{'s' if days > 1 else ''} ago"

def format_stage_label(stage: Optional[str], status: Optional[str]) -> str:
    norm_status = (status or "").lower()
    norm_stage = (stage or "").lower()
    if norm_status == "completed" or norm_stage == "complete":
        return "Complete"
    if norm_status == "failed":
        return f"Failed at {stage or 'processing'}"
    stage_map = {
        "upload": "Uploaded",
        "queued": "Queued",
        "transcribing": "Transcribing",
        "speaker_detection": "Identifying speakers",
        "chunking": "Temporal chunking",
        "embedding": "Generating embeddings",
        "indexing": "Vector indexing",
    }
    return stage_map.get(norm_stage, (stage or "Processing").capitalize())

def enrich_job_response(job: ProcessingJob) -> ProcessingJobResponse:
    resp = ProcessingJobResponse.model_validate(job)
    resp.episode_title = job.episode.title if job.episode else "Untitled Episode"
    resp.started_formatted = format_time_ago(job.started_at or job.created_at)
    if job.completed_at and job.started_at:
        diff_sec = int((job.completed_at - job.started_at).total_seconds())
        m = diff_sec // 60
        s = diff_sec % 60
        resp.duration_formatted = f"{m:02d}:{s:02d}"
    else:
        resp.duration_formatted = "-"
    return resp

@router.get("/jobs", response_model=List[ProcessingJobResponse])
def get_processing_jobs(
    limit: int = Query(50, ge=1, le=100),
    processing_repo: ProcessingRepository = Depends(get_processing_repo),
):
    jobs = processing_repo.get_all_jobs(limit=limit)
    return [enrich_job_response(j) for j in jobs]

@router.get("/jobs/{id}", response_model=ProcessingJobResponse)
def get_processing_job(
    id: str,
    processing_repo: ProcessingRepository = Depends(get_processing_repo),
):
    job = processing_repo.get_by_id(id)
    if not job:
        raise NotFoundException("ProcessingJob", id)
    return enrich_job_response(job)

@router.post("/jobs/{id}/retry", response_model=ProcessingJobResponse)
def retry_processing_job(
    id: str,
    background_tasks: BackgroundTasks,
    processing_repo: ProcessingRepository = Depends(get_processing_repo),
):
    job = processing_repo.get_by_id(id)
    if not job:
        raise NotFoundException("ProcessingJob", id)

    job.status = "queued"
    job.current_stage = "queued"
    job.progress = 0
    job.error_message = None
    processing_repo.update(job)

    # Trigger background worker
    background_tasks.add_task(pipeline_processor.run, job.episode_id, job.id)
    return enrich_job_response(job)

@router.post("/jobs/{id}/cancel", response_model=ProcessingJobResponse)
def cancel_processing_job(
    id: str,
    processing_repo: ProcessingRepository = Depends(get_processing_repo),
    episode_repo: EpisodeRepository = Depends(get_episode_repo),
):
    job = processing_repo.get_by_id(id)
    if not job:
        raise NotFoundException("ProcessingJob", id)

    job.status = "failed"
    job.error_message = "Cancelled by user"
    processing_repo.update(job)

    if job.episode_id:
        episode = episode_repo.get_by_id(job.episode_id)
        if episode and episode.status != "completed":
            episode.status = "failed"
            episode_repo.update(episode)

    return enrich_job_response(job)

@router.get("/episodes/{episode_id}/jobs", response_model=List[ProcessingJobResponse])
def get_episode_processing_jobs(
    episode_id: str,
    processing_repo: ProcessingRepository = Depends(get_processing_repo),
):
    jobs = processing_repo.get_jobs_by_episode(episode_id)
    return [enrich_job_response(j) for j in jobs]

@router.get("/stats")
def get_processing_stats(
    processing_repo: ProcessingRepository = Depends(get_processing_repo),
):
    active_jobs = processing_repo.get_active_jobs()
    return {
        "active_jobs_count": len(active_jobs),
        "has_active_jobs": len(active_jobs) > 0,
    }
