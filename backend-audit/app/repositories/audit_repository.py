from sqlalchemy.orm import Session
from app.models.audit import AuditLog

class AuditRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_logs(self, limit: int = 50):
        return self.db.query(AuditLog).order_by(AuditLog.created_at.desc()).limit(limit).all()
