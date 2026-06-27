from sqlalchemy.orm import Session
from app.models.item import Item

class ItemRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self, skip: int = 0, limit: int = 100):
        return self.db.query(Item).offset(skip).limit(limit).all()

    def get_by_id(self, item_id: int):
        return self.db.query(Item).filter(Item.id == item_id).first()

    def create(self, name: str, description: str):
        new_item = Item(name=name, description=description, completed=False)
        self.db.add(new_item)
        self.db.commit()
        self.db.refresh(new_item)
        return new_item

    def update_status(self, item: Item, completed: bool):
        item.completed = completed
        self.db.commit()
        self.db.refresh(item)
        return item

    def delete(self, item: Item):
        self.db.delete(item)
        self.db.commit()
