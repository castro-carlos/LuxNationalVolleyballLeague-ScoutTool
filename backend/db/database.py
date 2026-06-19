import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

load_dotenv()


ENV = os.getenv("ENVIRONMENT", "local").lower()

if ENV == "production":
    DB_HOST = os.getenv("NEON_DB_HOST")
    DB_PORT = os.getenv("NEON_DB_PORT")
    DB_USER = os.getenv("NEON_DB_USER")
    DB_PASSWORD = os.getenv("NEON_DB_PASSWORD")
    DB_NAME = os.getenv("NEON_DB_NAME")
else:
    DB_HOST = os.getenv("LOCAL_DB_HOST")
    DB_PORT = os.getenv("LOCAL_DB_PORT")
    DB_USER = os.getenv("LOCAL_DB_USER")
    DB_PASSWORD = os.getenv("LOCAL_DB_PASSWORD")
    DB_NAME = os.getenv("LOCAL_DB_NAME")

DB_CONN_STRING = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

#Handle SSL configurations automatically
connect_args = {}
if "neon.tech" in (DB_HOST or ""):
    connect_args["ssl"] = "require"

engine = create_async_engine(DB_CONN_STRING, connect_args=connect_args, echo=True)

AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

async def get_db():
    async with AsyncSessionLocal() as session:  # Use 'async with' to automatically open/close
        try:
            yield session
        finally:
            await session.close()  # Await the database clean-up asynchronously