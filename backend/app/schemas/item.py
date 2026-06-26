from pydantic import BaseModel
from datetime import datetime

class ItemBase(BaseModel):
    name: str
    description: str

class ItemCreate(ItemBase):
    pass

class ItemUpdate(BaseModel):
    completed: bool

class ItemResponse(ItemBase):
    id: int
    completed: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
