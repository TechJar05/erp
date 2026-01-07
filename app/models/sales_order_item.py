from sqlalchemy import Column, Numeric, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base
import uuid

class SalesOrderItem(Base):
    __tablename__ = "sales_order_item"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sales_order_id = Column(UUID(as_uuid=True), ForeignKey("sales_order.id"), nullable=False)
    item_id = Column(UUID(as_uuid=True), ForeignKey("item.id"), nullable=False)
    ordered_qty = Column(Numeric, nullable=False)
    shipped_qty = Column(Numeric, default=0)
