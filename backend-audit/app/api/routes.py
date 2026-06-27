from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.services.audit_service import AuditService
from app.schemas.audit import AuditLogResponse

router = APIRouter()

@router.get("/")
def read_root():
    return {"status": "ok", "message": "Audit Service API is running!"}

@router.get("/api/audit", response_model=List[AuditLogResponse])
def read_audit(limit: int = 50, db: Session = Depends(get_db)):
    service = AuditService(db)
    return service.get_audit_logs(limit)
