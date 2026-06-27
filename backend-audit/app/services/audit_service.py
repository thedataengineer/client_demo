from sqlalchemy.orm import Session
from app.repositories.audit_repository import AuditRepository

class AuditService:
    def __init__(self, db: Session):
        self.repo = AuditRepository(db)

    def get_audit_logs(self, limit: int = 50):
        return self.repo.get_logs(limit)
