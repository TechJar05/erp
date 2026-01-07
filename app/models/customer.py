from sqlalchemy import Column, Text, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.core.database import Base
import uuid

class Customer(Base):
    __tablename__ = "customer"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(Text, nullable=False)
    region = Column(Text)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
