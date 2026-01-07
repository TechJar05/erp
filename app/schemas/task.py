from pydantic import BaseModel
from uuid import UUID
from typing import Optional

class TaskResponse(BaseModel):
    id: UUID
    task_type: str
    reference_type: str
    reference_name: Optional[str]
    priority: str
    status: str

    class Config:
        from_attributes = True
