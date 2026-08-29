from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class ProjectResponse(ProjectBase):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime
    episodes_count: Optional[int] = 0
    total_duration_formatted: Optional[str] = "0m"

    model_config = ConfigDict(from_attributes=True)
