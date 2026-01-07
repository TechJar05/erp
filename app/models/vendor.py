from sqlalchemy import Column, Text, Numeric, Integer, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base
import uuid
from sqlalchemy.sql import func

class Vendor(Base):
    __tablename__ = "vendor"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(Text, nullable=False)
    location = Column(Text)
    rating = Column(Numeric)
    lead_time_days = Column(Integer)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
