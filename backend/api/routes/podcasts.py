from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from backend.core.database import get_db
from backend.api.dependencies import get_podcast_repo, get_episode_repo
from backend.repositories.podcast_repo import PodcastRepository
from backend.repositories.episode_repo import EpisodeRepository
from backend.models.podcast import Podcast
from backend.schemas.podcast_schemas import (
    PodcastResponse, PodcastCreate, PodcastUpdate, PodcastListResponse,
    PodcastImportRequest, PodcastImportResponse
)
from backend.schemas.episode_schemas import EpisodeResponse
from backend.api.routes.episodes import enrich_episode_response
from backend.services.podcast_ingestion_service import podcast_ingestion_service
from backend.core.exceptions import NotFoundException

router = APIRouter(prefix="/podcasts", tags=["podcasts"])

def enrich_podcast_response(podcast: Podcast) -> PodcastResponse:
    resp = PodcastResponse.model_validate(podcast)
    resp.episode_count = len(podcast.episodes) if podcast.episodes else 0
    return resp

@router.post("/import", response_model=PodcastImportResponse, status_code=200)
async def import_podcast_feed(
    request: PodcastImportRequest,
    db: Session = Depends(get_db),
):
    """
    Imports podcast show metadata and its episodes from an RSS/Atom feed URL.
    Performs SSRF validation, deduplication, and stores metadata in the database.
    """
    result = await podcast_ingestion_service.ingest_feed_url(
        db=db,
        feed_url=request.feed_url,
        project_id=request.project_id,
    )
    podcast = result["podcast"]
    return PodcastImportResponse(
        podcast=enrich_podcast_response(podcast),
        total_episodes_in_feed=result["total_episodes_in_feed"],
        new_episodes_imported=result["new_episodes_imported"],
        updated_episodes=result["updated_episodes"],
        message=f"Successfully imported '{podcast.title}' with {result['new_episodes_imported']} new episodes.",
    )

@router.get("", response_model=List[PodcastResponse])
def list_podcasts(
    q: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    podcast_repo: PodcastRepository = Depends(get_podcast_repo),
):
    podcasts = podcast_repo.get_podcasts(query=q, skip=skip, limit=limit)
    return [enrich_podcast_response(p) for p in podcasts]

@router.post("", response_model=PodcastResponse, status_code=201)
def create_podcast(
    podcast_in: PodcastCreate,
    podcast_repo: PodcastRepository = Depends(get_podcast_repo),
):
    # Check for existing feed_url if provided
    if podcast_in.feed_url:
        existing = podcast_repo.get_by_feed_url(podcast_in.feed_url)
        if existing:
            return enrich_podcast_response(existing)

    podcast = Podcast(**podcast_in.model_dump())
    created = podcast_repo.create(podcast)
    return enrich_podcast_response(created)

@router.get("/{id}", response_model=PodcastResponse)
def get_podcast(
    id: str,
    podcast_repo: PodcastRepository = Depends(get_podcast_repo),
):
    podcast = podcast_repo.get_by_id(id)
    if not podcast:
        raise NotFoundException("Podcast", id)
    return enrich_podcast_response(podcast)

@router.patch("/{id}", response_model=PodcastResponse)
def update_podcast(
    id: str,
    updates: PodcastUpdate,
    podcast_repo: PodcastRepository = Depends(get_podcast_repo),
):
    podcast = podcast_repo.get_by_id(id)
    if not podcast:
        raise NotFoundException("Podcast", id)

    update_data = updates.model_dump(exclude_unset=True)
    for k, v in update_data.items():
        setattr(podcast, k, v)

    updated = podcast_repo.update(podcast)
    return enrich_podcast_response(updated)

@router.delete("/{id}")
def delete_podcast(
    id: str,
    podcast_repo: PodcastRepository = Depends(get_podcast_repo),
):
    podcast = podcast_repo.get_by_id(id)
    if not podcast:
        raise NotFoundException("Podcast", id)
    podcast_repo.delete(id)
    return {"message": "Podcast deleted successfully", "id": id}

@router.get("/{id}/episodes", response_model=List[EpisodeResponse])
def get_podcast_episodes(
    id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    podcast_repo: PodcastRepository = Depends(get_podcast_repo),
):
    podcast = podcast_repo.get_by_id(id)
    if not podcast:
        raise NotFoundException("Podcast", id)

    episodes = podcast_repo.get_episodes(id, skip=skip, limit=limit)
    return [enrich_episode_response(ep) for ep in episodes]
