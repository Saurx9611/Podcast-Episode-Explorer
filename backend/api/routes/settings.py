from typing import Any, Dict
from fastapi import APIRouter, Depends, Body
from backend.api.dependencies import get_user_repo, get_current_user_id
from backend.repositories.user_repo import UserRepository
from backend.schemas.user_schemas import UserResponse, UserUpdate
from backend.core.exceptions import NotFoundException

router = APIRouter(prefix="/settings", tags=["settings"])

@router.get("", response_model=UserResponse)
def get_user_settings(
    user_repo: UserRepository = Depends(get_user_repo),
    user_id: str = Depends(get_current_user_id),
):
    user = user_repo.get_by_id(user_id) if user_id else None
    if not user:
        user = user_repo.get_or_create_default_user()
    return UserResponse.model_validate(user)

@router.patch("", response_model=UserResponse)
def update_user_settings(
    updates: UserUpdate,
    user_repo: UserRepository = Depends(get_user_repo),
    user_id: str = Depends(get_current_user_id),
):
    user = user_repo.get_by_id(user_id) if user_id else None
    if not user:
        user = user_repo.get_or_create_default_user()
    
    if updates.name is not None:
        user.name = updates.name
    if updates.role is not None:
        user.role = updates.role
    if updates.avatar_url is not None:
        user.avatar_url = updates.avatar_url
    if updates.preferences is not None:
        current_prefs = dict(user.preferences or {})
        current_prefs.update(updates.preferences)
        user.preferences = current_prefs
        
    user_repo.update(user)
    return UserResponse.model_validate(user)
