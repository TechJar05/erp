from sqlalchemy import Column, Text
from app.core.database import Base

class MetricMetadata(Base):
    __tablename__ = "metric_metadata"

    metric_name = Column(Text, primary_key=True)
    title = Column(Text, nullable=False)
    widget_type = Column(Text, nullable=False)
    chart_type = Column(Text)
    unit = Column(Text)
