from sqlalchemy import Column, Text
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base
import uuid

class Role(Base):
    __tablename__ = "role"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(Text, unique=True, nullable=False)
