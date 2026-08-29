from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from backend.api.dependencies import get_db, get_current_user_id
from backend.schemas.project_schemas import ProjectResponse, ProjectCreate, ProjectUpdate
from backend.repositories.project_repo import ProjectRepository
from backend.models import Project

router = APIRouter(prefix="/projects", tags=["projects"])

@router.get("", response_model=List[ProjectResponse])
def get_projects(db: Session = Depends(get_db), user_id: str = Depends(get_current_user_id)):
    repo = ProjectRepository(db)
    return repo.get_projects_by_user(user_id)

@router.post("", response_model=ProjectResponse)
def create_project(project: ProjectCreate, db: Session = Depends(get_db), user_id: str = Depends(get_current_user_id)):
    repo = ProjectRepository(db)
    new_project = Project(
        user_id=user_id,
        name=project.name,
        description=project.description
    )
    return repo.create_project(new_project)

@router.get("/{id}", response_model=ProjectResponse)
def get_project(id: str, db: Session = Depends(get_db), user_id: str = Depends(get_current_user_id)):
    repo = ProjectRepository(db)
    project = repo.get_project(id)
    if not project or project.user_id != user_id:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@router.patch("/{id}", response_model=ProjectResponse)
def update_project(id: str, updates: ProjectUpdate, db: Session = Depends(get_db), user_id: str = Depends(get_current_user_id)):
    repo = ProjectRepository(db)
    project = repo.get_project(id)
    if not project or project.user_id != user_id:
        raise HTTPException(status_code=404, detail="Project not found")
        
    update_data = updates.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(project, key, value)
        
    db.commit()
    db.refresh(project)
    return project

@router.delete("/{id}")
def delete_project(id: str, db: Session = Depends(get_db), user_id: str = Depends(get_current_user_id)):
    repo = ProjectRepository(db)
    project = repo.get_project(id)
    if not project or project.user_id != user_id:
        raise HTTPException(status_code=404, detail="Project not found")
        
    repo.delete_project(id)
    return {"message": "Project deleted successfully"}
