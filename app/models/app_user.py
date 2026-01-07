from sqlalchemy import Column, Text, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.core.database import Base
import uuid

class AppUser(Base):
    __tablename__ = "app_user"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(Text, nullable=False)
    role_id = Column(UUID(as_uuid=True), ForeignKey("role.id"))
    plant_id = Column(UUID(as_uuid=True), ForeignKey("plant.id"))
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
