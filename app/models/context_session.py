from sqlalchemy import Column, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.core.database import Base
import uuid

class ContextSession(Base):
    __tablename__ = "context_session"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    data_context_id = Column(UUID(as_uuid=True), ForeignKey("data_context.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("app_user.id"), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    last_active_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
