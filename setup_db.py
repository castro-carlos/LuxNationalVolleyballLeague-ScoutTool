import logging
from db.database import engine
from db.models import Base

# --- LOGGING CONFIGURATION ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler("database_setup.log", mode="a", encoding="utf-8"),
        logging.StreamHandler()
    ]
)

# --- DATABASE INITIALIZATION TARGET ---
def initialize_database():
    logging.info("Connecting to PostgreSQL via SQLAlchemy to initialize schema...")
    try:
        Base.metadata.create_all(engine)
        logging.info("Database tables initialized successfully via SQLAlchemy!")
    except Exception as e:
        logging.critical("FAILED to initialize database tables.", exc_info=True)

if __name__ == "__main__":
    initialize_database()