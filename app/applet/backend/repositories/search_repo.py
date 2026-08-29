from sqlalchemy.orm import Session
from sqlalchemy import text
from backend.models import SavedSearch
from backend.schemas.search_schemas import SavedSearchCreate, SavedSearchUpdate
from typing import List, Optional

class SearchRepository:
    def __init__(self, db: Session):
        self.db = db
        
    def get_saved_searches(self, user_id: str) -> List[SavedSearch]:
        return self.db.query(SavedSearch).filter(SavedSearch.user_id == user_id).order_by(SavedSearch.created_at.desc()).all()
        
    def get_saved_search(self, search_id: str) -> Optional[SavedSearch]:
        return self.db.query(SavedSearch).filter(SavedSearch.id == search_id).first()
        
    def create_saved_search(self, user_id: str, search: SavedSearchCreate) -> SavedSearch:
        db_search = SavedSearch(
            user_id=user_id,
            name=search.name,
            description=search.description,
            query=search.query,
            filters=search.filters
        )
        self.db.add(db_search)
        self.db.commit()
        self.db.refresh(db_search)
        return db_search
        
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
        
    def delete_saved_search(self, search_id: str) -> bool:
        search = self.get_saved_search(search_id)
        if search:
            self.db.delete(search)
            self.db.commit()
            return True
        return False
