from sqlalchemy import Column, Numeric, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base
import uuid

from sqlalchemy import UniqueConstraint

class VendorItem(Base):
    __tablename__ = "vendor_item"

    __table_args__ = (
        UniqueConstraint('vendor_id', 'item_id'),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    vendor_id = Column(UUID(as_uuid=True), ForeignKey("vendor.id"), nullable=False)
    item_id = Column(UUID(as_uuid=True), ForeignKey("item.id"), nullable=False)
    unit_price = Column(Numeric, nullable=False)