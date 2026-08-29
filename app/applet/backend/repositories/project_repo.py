from sqlalchemy.orm import Session
from backend.models import Project
from typing import List, Optional

class ProjectRepository:
    def __init__(self, db: Session):
        self.db = db
        
    def create_project(self, project: Project) -> Project:
        self.db.add(project)
        self.db.commit()
        self.db.refresh(project)
        return project
        
    def get_project(self, project_id: str) -> Optional[Project]:
        return self.db.query(Project).filter(Project.id == project_id).first()
        
    def get_projects_by_user(self, user_id: str) -> List[Project]:
        return self.db.query(Project).filter(Project.user_id == user_id).all()
        
    def delete_project(self, project_id: str) -> bool:
        project = self.get_project(project_id)
        if project:
            self.db.delete(project)
            self.db.commit()
            return True
        return False
