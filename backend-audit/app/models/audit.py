from sqlalchemy import Column, Integer, String, DateTime, Index
from datetime import datetime
from app.core.database import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True, index=True)
    table_name = Column(String, index=True)
    action = Column(String, index=True)
    record_id = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index('ix_audit_table_action', 'table_name', 'action'),
    )
