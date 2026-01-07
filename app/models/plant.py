from sqlalchemy import Column, Text, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base
import uuid
from sqlalchemy.sql import func

class Plant(Base):
    __tablename__ = "plant"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organization.id"), nullable=False)
    name = Column(Text, nullable=False)
    location = Column(Text)
    timezone = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
