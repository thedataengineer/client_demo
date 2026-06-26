import os
from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, Index, text
from sqlalchemy.orm import declarative_base, sessionmaker, Session

# Environment variables for DB configuration
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")
POSTGRES_DB = os.getenv("POSTGRES_DB", "app_db")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "db")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")

DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

# SQLAlchemy Setup
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Models
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

# Create tables (In a real app, use Alembic migrations)
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

# Inject raw DDL for triggers
with engine.begin() as conn:
    conn.execute(text("""
    CREATE OR REPLACE FUNCTION audit_trigger_func()
    RETURNS trigger AS $$
    BEGIN
        IF TG_OP = 'INSERT' THEN
            INSERT INTO audit_logs (table_name, action, record_id, created_at)
            VALUES (TG_TABLE_NAME, 'INSERT', NEW.id, NOW());
            RETURN NEW;
        ELSIF TG_OP = 'UPDATE' THEN
            INSERT INTO audit_logs (table_name, action, record_id, created_at)
            VALUES (TG_TABLE_NAME, 'UPDATE', NEW.id, NOW());
            RETURN NEW;
        ELSIF TG_OP = 'DELETE' THEN
            INSERT INTO audit_logs (table_name, action, record_id, created_at)
            VALUES (TG_TABLE_NAME, 'DELETE', OLD.id, NOW());
            RETURN OLD;
        END IF;
        RETURN NULL;
    END;
    $$ LANGUAGE plpgsql;
    """))
    
    conn.execute(text("DROP TRIGGER IF EXISTS audit_items_trigger ON items;"))
    conn.execute(text("""
    CREATE TRIGGER audit_items_trigger
    AFTER INSERT OR UPDATE OR DELETE ON items
    FOR EACH ROW EXECUTE FUNCTION audit_trigger_func();
    """))

# FastAPI App
app = FastAPI(title="Full Stack App API")

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Backend API is running!"}

@app.get("/api/items")
def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items = db.query(Item).offset(skip).limit(limit).all()
    return items

@app.post("/api/items")
def create_item(name: str, description: str, db: Session = Depends(get_db)):
    new_item = Item(name=name, description=description, completed=False)
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item

@app.put("/api/items/{item_id}")
def update_item_status(item_id: int, completed: bool, db: Session = Depends(get_db)):
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    item.completed = completed
    db.commit()
    db.refresh(item)
    return item

@app.delete("/api/items/{item_id}")
def delete_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(item)
    db.commit()
    return {"status": "ok"}

@app.get("/api/audit")
def read_audit(limit: int = 50, db: Session = Depends(get_db)):
    logs = db.query(AuditLog).order_by(AuditLog.created_at.desc()).limit(limit).all()
    return logs
