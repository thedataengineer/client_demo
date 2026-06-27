from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.services.item_service import ItemService
from app.schemas.item import ItemResponse

router = APIRouter()

@router.get("/")
def read_root():
    return {"status": "ok", "message": "Backend API is running!"}

@router.get("/api/items", response_model=List[ItemResponse])
def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    service = ItemService(db)
    return service.get_items(skip, limit)

@router.post("/api/items", response_model=ItemResponse)
def create_item(name: str, description: str, db: Session = Depends(get_db)):
    service = ItemService(db)
    return service.create_item(name, description)

@router.put("/api/items/{item_id}", response_model=ItemResponse)
def update_item_status(item_id: int, completed: bool, db: Session = Depends(get_db)):
    service = ItemService(db)
    return service.update_item_status(item_id, completed)

@router.delete("/api/items/{item_id}")
def delete_item(item_id: int, db: Session = Depends(get_db)):
    service = ItemService(db)
    service.delete_item(item_id)
    return {"status": "ok"}
