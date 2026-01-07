from sqlalchemy import Column, Numeric, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base
import uuid

class PurchaseOrderItem(Base):
    __tablename__ = "purchase_order_item"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    purchase_order_id = Column(UUID(as_uuid=True), ForeignKey("purchase_order.id"), nullable=False)
    item_id = Column(UUID(as_uuid=True), ForeignKey("item.id"), nullable=False)
    ordered_qty = Column(Numeric, nullable=False)
    received_qty = Column(Numeric, default=0)
    unit_price = Column(Numeric, nullable=False)
