from sqlalchemy import Column, Numeric, Text, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base
import uuid

class ProductionOrder(Base):
    __tablename__ = "production_order"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    item_id = Column(UUID(as_uuid=True), ForeignKey("item.id"), nullable=False)
    machine_id = Column(UUID(as_uuid=True), ForeignKey("machine.id"))
    planned_qty = Column(Numeric, nullable=False)
    actual_qty = Column(Numeric)
    start_date = Column(TIMESTAMP(timezone=True))
    end_date = Column(TIMESTAMP(timezone=True))
    status = Column(Text)
