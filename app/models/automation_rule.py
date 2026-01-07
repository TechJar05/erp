from sqlalchemy import Column, Text, Numeric, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.core.database import Base
import uuid

class AutomationRule(Base):
    __tablename__ = "automation_rule"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    data_context_id = Column(UUID(as_uuid=True), ForeignKey("data_context.id"), nullable=False)
    metric_name = Column(Text, nullable=False)
    condition = Column(Text, nullable=False)
    threshold = Column(Numeric, nullable=False)
    task_type = Column(Text, nullable=False)
    priority = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
