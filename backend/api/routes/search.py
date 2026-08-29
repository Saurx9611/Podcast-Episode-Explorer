from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from backend.api.dependencies import get_search_repo, get_episode_repo, get_current_user_id, get_db
from backend.repositories.search_repo import SearchRepository
from backend.repositories.episode_repo import EpisodeRepository
from backend.schemas.search_schemas import (
    SearchRequest, SearchResponse, SearchResultItem,
    SavedSearchResponse, SavedSearchCreate, SavedSearchUpdate
)
from backend.services.semantic_search_service import semantic_search_service
from backend.core.exceptions import NotFoundException

router = APIRouter(prefix="/search", tags=["search"])

@router.post("", response_model=SearchResponse)
async def search_episodes(
    request: SearchRequest,
    db: Session = Depends(get_db),
):
    return await semantic_search_service.search(db=db, request=request)

@router.get("/saved", response_model=List[SavedSearchResponse])
def get_saved_searches(
    search_repo: SearchRepository = Depends(get_search_repo),
    user_id: str = Depends(get_current_user_id),
):
    searches = search_repo.get_saved_searches(user_id)
    results = []
    for s in searches:
        resp = SavedSearchResponse.model_validate(s)
        resp.last_run_formatted = s.last_run_at.strftime("%b %d, %Y") if s.last_run_at else "Never"
        results.append(resp)
    return results

@router.post("/saved", response_model=SavedSearchResponse)
def create_saved_search(
    search_in: SavedSearchCreate,
    search_repo: SearchRepository = Depends(get_search_repo),
    user_id: str = Depends(get_current_user_id),
):
    saved = search_repo.create_saved_search(user_id, search_in)
    resp = SavedSearchResponse.model_validate(saved)
    resp.last_run_formatted = "Never"
    return resp

@router.get("/saved/{id}", response_model=SavedSearchResponse)
def get_saved_search(
    id: str,
    search_repo: SearchRepository = Depends(get_search_repo),
    user_id: str = Depends(get_current_user_id),
):
    search = search_repo.get_saved_search(id)
    if not search or search.user_id != user_id:
        raise NotFoundException("SavedSearch", id)
    resp = SavedSearchResponse.model_validate(search)
    resp.last_run_formatted = search.last_run_at.strftime("%b %d, %Y") if search.last_run_at else "Never"
    return resp

@router.patch("/saved/{id}", response_model=SavedSearchResponse)
def update_saved_search(
    id: str,
    updates: SavedSearchUpdate,
    search_repo: SearchRepository = Depends(get_search_repo),
    user_id: str = Depends(get_current_user_id),
):
    search = search_repo.get_saved_search(id)
    if not search or search.user_id != user_id:
        raise NotFoundException("SavedSearch", id)
    updated = search_repo.update_saved_search(id, updates)
    resp = SavedSearchResponse.model_validate(updated)
    resp.last_run_formatted = updated.last_run_at.strftime("%b %d, %Y") if updated.last_run_at else "Never"
    return resp

@router.delete("/saved/{id}")
def delete_saved_search(
    id: str,
    search_repo: SearchRepository = Depends(get_search_repo),
    user_id: str = Depends(get_current_user_id),
):
    search = search_repo.get_saved_search(id)
    if not search or search.user_id != user_id:
        raise NotFoundException("SavedSearch", id)
    search_repo.delete(id)
    return {"message": "Saved search deleted successfully", "id": id}

@router.post("/saved/{id}/run", response_model=SearchResponse)
async def run_saved_search(
    id: str,
    search_repo: SearchRepository = Depends(get_search_repo),
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    search = search_repo.get_saved_search(id)
    if not search or search.user_id != user_id:
        raise NotFoundException("SavedSearch", id)
    
    # Record run
    search_repo.record_search_run(id)
    
    # Execute semantic search
    req = SearchRequest(query=search.query)
    return await semantic_search_service.search(db=db, request=req)
