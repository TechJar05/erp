from sqlalchemy import Column, Date, Text, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.core.database import Base
import uuid

class SalesOrder(Base):
    __tablename__ = "sales_order"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customer.id"), nullable=False)
    order_date = Column(Date, nullable=False)
    promised_date = Column(Date)
    status = Column(Text)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
