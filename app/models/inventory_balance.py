from sqlalchemy import Column, Numeric, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base
import uuid
from sqlalchemy.sql import func

from sqlalchemy import UniqueConstraint

class InventoryBalance(Base):
    __tablename__ = "inventory_balance"

    __table_args__ = (
        UniqueConstraint('item_id', 'warehouse_id'),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    item_id = Column(UUID(as_uuid=True), ForeignKey("item.id"), nullable=False)
    warehouse_id = Column(UUID(as_uuid=True), ForeignKey("warehouse.id"), nullable=False)
    quantity_on_hand = Column(Numeric, nullable=False)
    last_updated = Column(TIMESTAMP(timezone=True), server_default=func.now())