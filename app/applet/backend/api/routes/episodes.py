from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List

from backend.api.dependencies import get_db, get_current_user_id
from backend.schemas.episode_schemas import EpisodeResponse, EpisodeCreate, EpisodeUploadResponse, TranscriptSegmentResponse, SpeakerResponse, EpisodeInsightResponse
from backend.repositories.episode_repo import EpisodeRepository
from backend.models import Episode, ProcessingJob
# We'll import services later
# from backend.services.audio_storage import AudioStorageService
# from backend.workers.processor import process_episode

router = APIRouter(prefix="/episodes", tags=["episodes"])

@router.post("", response_model=EpisodeUploadResponse)
async def upload_episode(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    project_id: str = Form(None),
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    repo = EpisodeRepository(db)
    # 1. Save file using storage service
    # audio_url, file_size, mime_type = AudioStorageService.save_file(file)
    
    # Mocking storage for now
    audio_url = f"/mock/storage/{file.filename}"
    file_size = 1024
    mime_type = file.content_type
    
    # 2. Create episode record
    episode = Episode(
        project_id=project_id,
        title=file.filename or "Untitled Episode",
        original_filename=file.filename,
        audio_url=audio_url,
        mime_type=mime_type,
        file_size=file_size,
        status="queued"
    )
    episode = repo.create_episode(episode)
    
    # 3. Create processing job record
    job = ProcessingJob(
        episode_id=episode.id,
        status="queued",
        current_stage="uploading",
        progress=0
    )
    db.add(job)
    db.commit()
    
    # 4. Queue background task
    # background_tasks.add_task(process_episode, episode.id, job.id)
    
    return {"id": episode.id, "status": "queued"}

@router.get("", response_model=List[EpisodeResponse])
def get_episodes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    repo = EpisodeRepository(db)
    return repo.get_episodes(skip=skip, limit=limit)

@router.get("/{id}", response_model=EpisodeResponse)
def get_episode(id: str, db: Session = Depends(get_db)):
    repo = EpisodeRepository(db)
    episode = repo.get_episode(id)
    if not episode:
        raise HTTPException(status_code=404, detail="Episode not found")
    return episode

@router.delete("/{id}")
def delete_episode(id: str, db: Session = Depends(get_db)):
    repo = EpisodeRepository(db)
    if not repo.delete_episode(id):
        raise HTTPException(status_code=404, detail="Episode not found")
    return {"message": "Episode deleted successfully"}

@router.get("/{id}/transcript", response_model=List[TranscriptSegmentResponse])
def get_transcript(id: str, db: Session = Depends(get_db)):
    repo = EpisodeRepository(db)
    # Check if episode exists
    if not repo.get_episode(id):
        raise HTTPException(status_code=404, detail="Episode not found")
    return repo.get_transcript(id)

@router.get("/{id}/speakers", response_model=List[SpeakerResponse])
def get_speakers(id: str, db: Session = Depends(get_db)):
    repo = EpisodeRepository(db)
    return repo.get_speakers(id)
    
@router.get("/{id}/insights", response_model=EpisodeInsightResponse)
def get_insights(id: str, db: Session = Depends(get_db)):
    repo = EpisodeRepository(db)
    insight = repo.get_insights(id)
    if not insight:
        raise HTTPException(status_code=404, detail="Insights not found or not generated yet")
    return insight
