from sqlalchemy import Column, Text, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base
import uuid
from sqlalchemy.sql import func

class Warehouse(Base):
    __tablename__ = "warehouse"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    plant_id = Column(UUID(as_uuid=True), ForeignKey("plant.id"), nullable=False)
    name = Column(Text, nullable=False)
    type = Column(Text)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
