from sqlalchemy import Column, Text, Numeric
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base
import uuid

class Machine(Base):
    __tablename__ = "machine"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    machine_code = Column(Text, unique=True, nullable=False)
    capacity_per_day = Column(Numeric, nullable=False)
    efficiency = Column(Numeric, default=1.0)
