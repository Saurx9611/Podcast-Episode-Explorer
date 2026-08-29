import os
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query, BackgroundTasks
from backend.api.dependencies import get_episode_repo, get_processing_repo, get_current_user_id
from backend.repositories.episode_repo import EpisodeRepository
from backend.repositories.processing_repo import ProcessingRepository
from backend.schemas.episode_schemas import (
    EpisodeResponse, EpisodeCreate, EpisodeUpdate, EpisodeUploadResponse,
    TranscriptSegmentResponse, SpeakerResponse, SpeakerUpdate, EpisodeInsightResponse
)
from backend.schemas.processing_schemas import ProcessingJobResponse
from backend.models.episode import Episode
from backend.models.processing_job import ProcessingJob
from backend.storage import storage_service
from backend.workers import pipeline_processor
from backend.services import insight_service
from backend.core.exceptions import NotFoundException

router = APIRouter(prefix="/episodes", tags=["episodes"])

def format_duration(seconds: Optional[float]) -> str:
    if not seconds or seconds <= 0:
        return "0:00"
    total_seconds = int(seconds)
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    secs = total_seconds % 60
    if hours > 0:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"

def format_file_size(size_bytes: Optional[int]) -> str:
    if not size_bytes:
        return "0 MB"
    mb = size_bytes / (1024 * 1024)
    return f"{mb:.1f} MB"

def format_date(dt: Optional[datetime]) -> str:
    if not dt:
        return "-"
    return dt.strftime("%b %d, %Y")

def enrich_episode_response(ep: Episode) -> EpisodeResponse:
    data = EpisodeResponse.model_validate(ep)
    data.project_name = ep.project.name if ep.project else "Unassigned"
    data.duration_formatted = format_duration(ep.duration)
    data.file_size_formatted = format_file_size(ep.file_size)
    data.date_formatted = format_date(ep.created_at)
    return data

@router.get("", response_model=List[EpisodeResponse])
def list_episodes(
    project_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    q: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    episode_repo: EpisodeRepository = Depends(get_episode_repo),
):
    episodes = episode_repo.get_episodes(
        project_id=project_id,
        status=status,
        query=q,
        skip=skip,
        limit=limit,
    )
    return [enrich_episode_response(ep) for ep in episodes]

@router.post("", response_model=EpisodeUploadResponse)
async def upload_episode(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    title: Optional[str] = Form(None),
    project_id: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    episode_repo: EpisodeRepository = Depends(get_episode_repo),
    processing_repo: ProcessingRepository = Depends(get_processing_repo),
    user_id: str = Depends(get_current_user_id),
):
    audio_url, orig_filename, file_size, mime_type = await storage_service.save_file(file)

    episode_title = title
    if not episode_title:
        base_name, _ = os.path.splitext(orig_filename)
        episode_title = base_name.replace("-", " ").replace("_", " ").title()

    episode = Episode(
        project_id=project_id if project_id and project_id != "none" else None,
        title=episode_title,
        description=description,
        original_filename=orig_filename,
        audio_url=audio_url,
        mime_type=mime_type,
        file_size=file_size,
        duration=0.0,
        status="queued",
    )
    created_ep = episode_repo.create(episode)

    job = ProcessingJob(
        episode_id=created_ep.id,
        status="queued",
        current_stage="upload",
        progress=0,
    )
    created_job = processing_repo.create(job)

    background_tasks.add_task(pipeline_processor.run, created_ep.id, created_job.id)

    return EpisodeUploadResponse(
        id=created_ep.id,
        status="queued",
        title=created_ep.title,
        message="Episode uploaded and queued for processing.",
    )

@router.get("/{id}", response_model=EpisodeResponse)
def get_episode(
    id: str,
    episode_repo: EpisodeRepository = Depends(get_episode_repo),
):
    episode = episode_repo.get_by_id(id)
    if not episode:
        raise NotFoundException("Episode", id)
    return enrich_episode_response(episode)

@router.post("/{id}/process", response_model=ProcessingJobResponse)
def process_episode(
    id: str,
    background_tasks: BackgroundTasks,
    episode_repo: EpisodeRepository = Depends(get_episode_repo),
    processing_repo: ProcessingRepository = Depends(get_processing_repo),
):
    episode = episode_repo.get_by_id(id)
    if not episode:
        raise NotFoundException("Episode", id)

    job = ProcessingJob(
        episode_id=episode.id,
        status="queued",
        current_stage="queued",
        progress=0,
    )
    created_job = processing_repo.create(job)

    episode.status = "queued"
    episode_repo.update(episode)

    background_tasks.add_task(pipeline_processor.run, episode.id, created_job.id)

    return ProcessingJobResponse.model_validate(created_job)

@router.get("/{id}/processing", response_model=ProcessingJobResponse)
def get_episode_processing_status(
    id: str,
    episode_repo: EpisodeRepository = Depends(get_episode_repo),
    processing_repo: ProcessingRepository = Depends(get_processing_repo),
):
    episode = episode_repo.get_by_id(id)
    if not episode:
        raise NotFoundException("Episode", id)

    jobs = processing_repo.get_jobs_by_episode(id)
    if not jobs:
        raise NotFoundException("ProcessingJob for Episode", id)

    job = jobs[0]
    resp = ProcessingJobResponse.model_validate(job)
    resp.episode_title = episode.title
    return resp

@router.patch("/{id}", response_model=EpisodeResponse)
def update_episode(
    id: str,
    updates: EpisodeUpdate,
    episode_repo: EpisodeRepository = Depends(get_episode_repo),
):
    episode = episode_repo.get_by_id(id)
    if not episode:
        raise NotFoundException("Episode", id)
    
    update_data = updates.model_dump(exclude_unset=True)
    for k, v in update_data.items():
        setattr(episode, k, v)
    
    updated = episode_repo.update(episode)
    return enrich_episode_response(updated)

@router.delete("/{id}")
def delete_episode(
    id: str,
    episode_repo: EpisodeRepository = Depends(get_episode_repo),
):
    episode = episode_repo.get_by_id(id)
    if not episode:
        raise NotFoundException("Episode", id)
    
    if episode.audio_url:
        storage_service.delete_file(episode.audio_url)

    episode_repo.delete(id)
    return {"message": "Episode deleted successfully", "id": id}

@router.get("/{id}/transcript", response_model=List[TranscriptSegmentResponse])
def get_episode_transcript(
    id: str,
    episode_repo: EpisodeRepository = Depends(get_episode_repo),
):
    episode = episode_repo.get_by_id(id)
    if not episode:
        raise NotFoundException("Episode", id)
    
    segments = episode_repo.get_transcript(id)
    results = []
    for s in segments:
        resp = TranscriptSegmentResponse.model_validate(s)
        resp.start = format_duration(s.start_time)
        resp.startSec = s.start_time
        results.append(resp)
    return results

@router.get("/{id}/speakers", response_model=List[SpeakerResponse])
def get_episode_speakers(
    id: str,
    episode_repo: EpisodeRepository = Depends(get_episode_repo),
):
    episode = episode_repo.get_by_id(id)
    if not episode:
        raise NotFoundException("Episode", id)
    speakers = episode_repo.get_speakers(id)
    return [SpeakerResponse.model_validate(s) for s in speakers]

@router.patch("/{id}/speakers/{speaker_id}", response_model=SpeakerResponse)
def rename_speaker(
    id: str,
    speaker_id: str,
    updates: SpeakerUpdate,
    episode_repo: EpisodeRepository = Depends(get_episode_repo),
):
    speaker = episode_repo.update_speaker(
        speaker_id=speaker_id,
        display_name=updates.display_name,
        label=updates.label,
    )
    if not speaker or speaker.episode_id != id:
        raise NotFoundException("Speaker", speaker_id)
    return SpeakerResponse.model_validate(speaker)

@router.get("/{id}/insights", response_model=EpisodeInsightResponse)
async def get_episode_insights(
    id: str,
    episode_repo: EpisodeRepository = Depends(get_episode_repo),
):
    episode = episode_repo.get_by_id(id)
    if not episode:
        raise NotFoundException("Episode", id)
    
    insight = episode_repo.get_insights(id)
    if not insight:
        segments = episode_repo.get_transcript(id)
        transcript_text = " ".join(s.text for s in segments)
        data = await insight_service.generate_insights(episode.title, transcript_text)
        insight = episode_repo.upsert_insights(
            episode_id=id,
            overview=data.get("overview"),
            competencies=data.get("competencies", []),
            technologies=data.get("technologies", []),
            architecture=data.get("architecture", []),
            resume_bullet=data.get("resume_bullet"),
        )
    return EpisodeInsightResponse.model_validate(insight)
