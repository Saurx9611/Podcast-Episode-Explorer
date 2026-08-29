from pydantic import BaseModel, Field
from typing import List, Optional, Any
from datetime import datetime

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
    # We might compute these dynamically or include them if needed
    episodes_count: Optional[int] = 0
    total_duration_formatted: Optional[str] = "0m"

    class Config:
        from_attributes = True
