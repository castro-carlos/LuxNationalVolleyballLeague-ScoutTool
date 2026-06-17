# database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from setup_db import DB_CONN_STRING

engine = create_engine(DB_CONN_STRING, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Centralized dependency used by all routers
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()