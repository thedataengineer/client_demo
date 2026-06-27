from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker
from app.core.config import settings

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
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
