from typing import List
from fastapi import APIRouter, Depends
from backend.api.dependencies import get_project_repo, get_current_user_id
from backend.repositories.project_repo import ProjectRepository
from backend.schemas.project_schemas import ProjectResponse, ProjectCreate, ProjectUpdate
from backend.models.project import Project
from backend.core.exceptions import NotFoundException

router = APIRouter(prefix="/projects", tags=["projects"])

@router.get("", response_model=List[ProjectResponse])
def list_projects(
    project_repo: ProjectRepository = Depends(get_project_repo),
    user_id: str = Depends(get_current_user_id),
):
    stats = project_repo.list_projects_with_stats(user_id)
    return [ProjectResponse(**s) for s in stats]

@router.post("", response_model=ProjectResponse)
def create_project(
    project_in: ProjectCreate,
    project_repo: ProjectRepository = Depends(get_project_repo),
    user_id: str = Depends(get_current_user_id),
):
    new_proj = Project(
        user_id=user_id,
        name=project_in.name,
        description=project_in.description,
    )
    created = project_repo.create(new_proj)
    stats = project_repo.get_project_with_stats(created.id)
    return ProjectResponse(**stats)

@router.get("/{id}", response_model=ProjectResponse)
def get_project(
    id: str,
    project_repo: ProjectRepository = Depends(get_project_repo),
    user_id: str = Depends(get_current_user_id),
):
    stats = project_repo.get_project_with_stats(id)
    if not stats or stats["user_id"] != user_id:
        raise NotFoundException("Project", id)
    return ProjectResponse(**stats)

@router.patch("/{id}", response_model=ProjectResponse)
def update_project(
    id: str,
    updates: ProjectUpdate,
    project_repo: ProjectRepository = Depends(get_project_repo),
    user_id: str = Depends(get_current_user_id),
):
    proj = project_repo.get_by_id(id)
    if not proj or proj.user_id != user_id:
        raise NotFoundException("Project", id)
    
    update_data = updates.model_dump(exclude_unset=True)
    for k, v in update_data.items():
        setattr(proj, k, v)
        
    project_repo.update(proj)
    stats = project_repo.get_project_with_stats(id)
    return ProjectResponse(**stats)

@router.delete("/{id}")
def delete_project(
    id: str,
    project_repo: ProjectRepository = Depends(get_project_repo),
    user_id: str = Depends(get_current_user_id),
):
    proj = project_repo.get_by_id(id)
    if not proj or proj.user_id != user_id:
        raise NotFoundException("Project", id)
    project_repo.delete(id)
    return {"message": "Project deleted successfully", "id": id}
