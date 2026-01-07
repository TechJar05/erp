from sqlalchemy import Column, Text, Numeric, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base
import uuid
from sqlalchemy.sql import func

class Item(Base):
    __tablename__ = "item"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sku = Column(Text, unique=True, nullable=False)
    name = Column(Text, nullable=False)
    item_type = Column(Text)
    uom = Column(Text, nullable=False)
    reorder_level = Column(Numeric, default=0)
    safety_stock = Column(Numeric, default=0)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
