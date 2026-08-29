from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.models.project import Project
from backend.models.episode import Episode
from backend.repositories.base_repo import BaseRepository

class ProjectRepository(BaseRepository[Project]):
    def __init__(self, db: Session):
        super().__init__(Project, db)

    def get_by_user_id(self, user_id: str) -> List[Project]:
        return self.db.query(Project).filter(Project.user_id == user_id).order_by(Project.updated_at.desc()).all()

    def get_project_with_stats(self, project_id: str) -> Optional[dict]:
        project = self.get_by_id(project_id)
        if not project:
            return None
        
        ep_count = self.db.query(func.count(Episode.id)).filter(Episode.project_id == project_id).scalar() or 0
        total_duration = self.db.query(func.sum(Episode.duration)).filter(Episode.project_id == project_id).scalar() or 0.0
        
        hours = int(total_duration // 3600)
        minutes = int((total_duration % 3600) // 60)
        duration_str = f"{hours}h {minutes}m" if hours > 0 else f"{minutes}m"

        return {
            "id": project.id,
            "user_id": project.user_id,
            "name": project.name,
            "description": project.description,
            "created_at": project.created_at,
            "updated_at": project.updated_at,
            "episodes_count": ep_count,
            "total_duration_formatted": duration_str,
        }

    def list_projects_with_stats(self, user_id: str) -> List[dict]:
        projects = self.get_by_user_id(user_id)
        results = []
        for p in projects:
            ep_count = len(p.episodes)
            total_duration = sum(ep.duration or 0.0 for ep in p.episodes)
            hours = int(total_duration // 3600)
            minutes = int((total_duration % 3600) // 60)
            duration_str = f"{hours}h {minutes}m" if hours > 0 else f"{minutes}m"
            results.append({
                "id": p.id,
                "user_id": p.user_id,
                "name": p.name,
                "description": p.description,
                "created_at": p.created_at,
                "updated_at": p.updated_at,
                "episodes_count": ep_count,
                "total_duration_formatted": duration_str,
            })
        return results
