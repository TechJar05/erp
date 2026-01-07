from sqlalchemy import Column, Text, Numeric, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base
import uuid
from sqlalchemy.sql import func

class InventoryTransaction(Base):
    __tablename__ = "inventory_transaction"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    item_id = Column(UUID(as_uuid=True), ForeignKey("item.id"), nullable=False)
    warehouse_id = Column(UUID(as_uuid=True), ForeignKey("warehouse.id"), nullable=False)
    transaction_type = Column(Text, nullable=False)
    quantity = Column(Numeric, nullable=False)
    reference_type = Column(Text)
    reference_id = Column(UUID(as_uuid=True))
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
