from sqlalchemy import Column, Integer, String, Boolean, DateTime, Index
from datetime import datetime
from app.core.database import Base

class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    completed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index('ix_items_name_desc', 'name', 'description'),
        Index('ix_item_status_time', 'completed', 'updated_at'),
    )
