from typing import List, Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from backend.models.processing_job import ProcessingJob
from backend.repositories.base_repo import BaseRepository

def utc_now():
    return datetime.now(timezone.utc)

class ProcessingRepository(BaseRepository[ProcessingJob]):
    def __init__(self, db: Session):
        super().__init__(ProcessingJob, db)

    def get_all_jobs(self, limit: int = 50) -> List[ProcessingJob]:
        from sqlalchemy.orm import joinedload
        return (
            self.db.query(ProcessingJob)
            .options(joinedload(ProcessingJob.episode))
            .order_by(ProcessingJob.started_at.desc())
            .limit(limit)
            .all()
        )

    def get_jobs_by_episode(self, episode_id: str) -> List[ProcessingJob]:
        from sqlalchemy.orm import joinedload
        return (
            self.db.query(ProcessingJob)
            .options(joinedload(ProcessingJob.episode))
            .filter(ProcessingJob.episode_id == episode_id)
            .order_by(ProcessingJob.started_at.desc())
            .all()
        )

    def get_by_episode_id(self, episode_id: str) -> Optional[ProcessingJob]:
        jobs = self.get_jobs_by_episode(episode_id)
        return jobs[0] if jobs else None

    def get_active_jobs(self) -> List[ProcessingJob]:
        return (
            self.db.query(ProcessingJob)
            .filter(ProcessingJob.status.in_(["queued", "processing"]))
            .all()
        )

    def update_progress(
        self,
        job_id: str,
        stage: str,
        progress: int,
        status: str = "processing",
        error_message: Optional[str] = None
    ) -> Optional[ProcessingJob]:
        job = self.get_by_id(job_id)
        if not job:
            return None
        job.current_stage = stage
        job.progress = progress
        job.status = status
        if error_message:
            job.error_message = error_message
        if status in ["completed", "failed"]:
            job.completed_at = utc_now()
        self.db.commit()
        self.db.refresh(job)
        return job
