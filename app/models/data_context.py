from sqlalchemy import Column, Text, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from app.core.database import Base
import uuid

class DataContext(Base):
    __tablename__ = "data_context"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(Text, nullable=False)
    context_type = Column(Text, nullable=False)
    primary_table = Column(Text, nullable=False)
    allowed_tables = Column(JSONB, nullable=False)
    allowed_columns = Column(JSONB, nullable=False)
    allowed_metrics = Column(JSONB, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
