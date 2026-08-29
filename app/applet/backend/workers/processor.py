from sqlalchemy.orm import Session
from backend.core.database import SessionLocal
from backend.models import Episode, ProcessingJob
import time

def process_episode(episode_id: str, job_id: str):
    db: Session = SessionLocal()
    try:
        job = db.query(ProcessingJob).filter(ProcessingJob.id == job_id).first()
        if not job:
            return
            
        stages = ["uploading", "transcription", "speaker_detection", "chunking", "embedding", "indexing", "complete"]
        
        for i, stage in enumerate(stages):
            job.current_stage = stage
            job.progress = int((i / (len(stages) - 1)) * 100)
            db.commit()
            
            # Simulate work
            time.sleep(1)
            
        job.status = "completed"
        db.commit()
        
    except Exception as e:
        job.status = "failed"
        job.error_message = str(e)
        db.commit()
    finally:
        db.close()
