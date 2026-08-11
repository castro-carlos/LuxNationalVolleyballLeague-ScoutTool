import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

load_dotenv()

# 1. Check if Docker Compose passed a full DATABASE_URL
DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    DB_CONN_STRING = DATABASE_URL
    connect_args = {}
else:
    # 2. Fallback to building string from individual variables
    ENVIRONMENT = os.getenv("ENVIRONMENT", "local")

if ENVIRONMENT == "local":
    user = os.getenv("POSTGRES_USER")
    pwd = os.getenv("POSTGRES_PASSWORD")
    host = os.getenv("POSTGRES_HOST", "db")
    port = os.getenv("POSTGRES_PORT", "5432")
    name = os.getenv("POSTGRES_DB")
else:
    user = os.getenv("NEON_DB_USER")
    pwd = os.getenv("NEON_DB_PASSWORD")
    host = os.getenv("NEON_DB_HOST")
    port = os.getenv("NEON_DB_PORT", "5432")
    name = os.getenv("NEON_DB_NAME")


print(f"--- DB DEBUG: host={host}, port={port}, user={user}, db={name} ---")
# Build the connection string cleanly for standard platforms
DB_CONN_STRING = f"postgresql+asyncpg://{user}:{pwd}@{host}:{port}/{name}"

# Neon requires SSL for production cloud setups
connect_args = {"ssl": "require"} if ENVIRONMENT != "local" else {}

# Standard global engine setup
engine = create_async_engine(DB_CONN_STRING, connect_args=connect_args, echo=True)
AsyncSessionFactory = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_db():
    async with AsyncSessionFactory() as session:
        try:
            yield session
        finally:
            await session.close()