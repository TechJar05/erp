from sqlalchemy import Column, Text, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.core.database import Base
import uuid

class Task(Base):
    __tablename__ = "task"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_type = Column(Text, nullable=False)
    reference_type = Column(Text)
    reference_id = Column(UUID(as_uuid=True), nullable=True)
    reference_name = Column(Text, nullable=True)

    priority = Column(Text)
    status = Column(Text)
    assigned_to = Column(UUID(as_uuid=True), ForeignKey("app_user.id"))
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
