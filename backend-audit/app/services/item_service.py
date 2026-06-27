from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.repositories.item_repository import ItemRepository

class ItemService:
    def __init__(self, db: Session):
        self.repo = ItemRepository(db)

    def get_items(self, skip: int = 0, limit: int = 100):
        return self.repo.get_all(skip, limit)

    def create_item(self, name: str, description: str):
        return self.repo.create(name, description)

    def update_item_status(self, item_id: int, completed: bool):
        item = self.repo.get_by_id(item_id)
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
        return self.repo.update_status(item, completed)

    def delete_item(self, item_id: int):
        item = self.repo.get_by_id(item_id)
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
        self.repo.delete(item)
