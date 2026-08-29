from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from backend.api.dependencies import get_db, get_current_user_id
from backend.schemas.search_schemas import SearchRequest, SearchResponse, SavedSearchResponse, SavedSearchCreate, SavedSearchUpdate
from backend.repositories.search_repo import SearchRepository
from backend.models import SavedSearch
# from backend.services.semantic_search_service import SemanticSearchService

router = APIRouter(prefix="/search", tags=["search"])

@router.post("", response_model=SearchResponse)
def perform_search(request: SearchRequest, db: Session = Depends(get_db)):
    # search_service = SemanticSearchService(db)
    # results = search_service.search(request)
    
    # Mocking for now
    return SearchResponse(
        query=request.query,
        results=[]
    )

@router.get("/saved", response_model=List[SavedSearchResponse])
def get_saved_searches(db: Session = Depends(get_db), user_id: str = Depends(get_current_user_id)):
    repo = SearchRepository(db)
    return repo.get_saved_searches(user_id)

@router.post("/saved", response_model=SavedSearchResponse)
def create_saved_search(search: SavedSearchCreate, db: Session = Depends(get_db), user_id: str = Depends(get_current_user_id)):
    repo = SearchRepository(db)
    return repo.create_saved_search(user_id, search)

@router.get("/saved/{id}", response_model=SavedSearchResponse)
def get_saved_search(id: str, db: Session = Depends(get_db), user_id: str = Depends(get_current_user_id)):
    repo = SearchRepository(db)
    search = repo.get_saved_search(id)
    if not search or search.user_id != user_id:
        raise HTTPException(status_code=404, detail="Saved search not found")
    return search

@router.patch("/saved/{id}", response_model=SavedSearchResponse)
def update_saved_search(id: str, updates: SavedSearchUpdate, db: Session = Depends(get_db), user_id: str = Depends(get_current_user_id)):
    repo = SearchRepository(db)
    search = repo.get_saved_search(id)
    if not search or search.user_id != user_id:
        raise HTTPException(status_code=404, detail="Saved search not found")
        
    return repo.update_saved_search(id, updates)

@router.delete("/saved/{id}")
def delete_saved_search(id: str, db: Session = Depends(get_db), user_id: str = Depends(get_current_user_id)):
    repo = SearchRepository(db)
    search = repo.get_saved_search(id)
    if not search or search.user_id != user_id:
        raise HTTPException(status_code=404, detail="Saved search not found")
        
    repo.delete_saved_search(id)
    return {"message": "Saved search deleted successfully"}

@router.post("/saved/{id}/run", response_model=SearchResponse)
def run_saved_search(id: str, db: Session = Depends(get_db), user_id: str = Depends(get_current_user_id)):
    repo = SearchRepository(db)
    search = repo.get_saved_search(id)
    if not search or search.user_id != user_id:
        raise HTTPException(status_code=404, detail="Saved search not found")
        
    # Build request from saved search
    req = SearchRequest(
        query=search.query,
        # Map filters if needed
    )
    
    # search_service = SemanticSearchService(db)
    # results = search_service.search(req)
    
    return SearchResponse(
        query=req.query,
        results=[]
    )
