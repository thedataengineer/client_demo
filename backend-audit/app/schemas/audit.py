from pydantic import BaseModel
from datetime import datetime

class AuditLogResponse(BaseModel):
    id: int
    table_name: str
    action: str
    record_id: int
    created_at: datetime

    class Config:
        from_attributes = True
