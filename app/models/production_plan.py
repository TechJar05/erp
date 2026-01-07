from sqlalchemy import Column, Date, Numeric, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base
import uuid

class ProductionPlan(Base):
    __tablename__ = "production_plan"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    item_id = Column(UUID(as_uuid=True), ForeignKey("item.id"), nullable=False)
    planned_qty = Column(Numeric, nullable=False)
    planned_date = Column(Date, nullable=False)
