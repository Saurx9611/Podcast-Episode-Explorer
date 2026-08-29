from typing import List, Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from backend.models.saved_search import SavedSearch
from backend.schemas.search_schemas import SavedSearchCreate, SavedSearchUpdate
from backend.repositories.base_repo import BaseRepository

def utc_now():
    return datetime.now(timezone.utc)

class SearchRepository(BaseRepository[SavedSearch]):
    def __init__(self, db: Session):
        super().__init__(SavedSearch, db)

    def get_saved_searches(self, user_id: str) -> List[SavedSearch]:
        return (
            self.db.query(SavedSearch)
            .filter(SavedSearch.user_id == user_id)
            .order_by(SavedSearch.created_at.desc())
            .all()
        )

    def get_saved_search(self, search_id: str) -> Optional[SavedSearch]:
        return self.get_by_id(search_id)

    def create_saved_search(self, user_id: str, search: SavedSearchCreate) -> SavedSearch:
        db_search = SavedSearch(
            user_id=user_id,
            name=search.name,
            description=search.description,
            query=search.query,
            filters=search.filters or [],
        )
        return self.create(db_search)

    def update_saved_search(self, search_id: str, updates: SavedSearchUpdate) -> Optional[SavedSearch]:
        search = self.get_saved_search(search_id)
        if not search:
            return None
            
        update_data = updates.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(search, key, value)
            
        self.db.commit()
        self.db.refresh(search)
        return search

    def record_search_run(self, search_id: str) -> Optional[SavedSearch]:
        search = self.get_saved_search(search_id)
        if not search:
            return None
        search.last_run_at = utc_now()
        search.run_count = (search.run_count or 0) + 1
        self.db.commit()
        self.db.refresh(search)
        return search
