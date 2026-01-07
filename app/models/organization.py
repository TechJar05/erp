from sqlalchemy import Column, Text, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base
import uuid
from sqlalchemy.sql import func

class Organization(Base):
    __tablename__ = "organization"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(Text, nullable=False)
    industry = Column(Text)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
