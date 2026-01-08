from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

class ContextSessionResponse(BaseModel):
    session_id: UUID
    context_id: UUID
    context_name: str
    created_at: datetime
    last_active_at: datetime

    class Config:
        from_attributes = True
