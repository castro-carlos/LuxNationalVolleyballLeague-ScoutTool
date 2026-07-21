import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

load_dotenv()

ENVIRONMENT = os.getenv("ENVIRONMENT", "production")

if ENVIRONMENT == "local":
    user = os.getenv("LOCAL_DB_USER")
    pwd = os.getenv("LOCAL_DB_PASSWORD")
    host = os.getenv("LOCAL_DB_HOST")
    port = os.getenv("LOCAL_DB_PORT", "5432")
    name = os.getenv("LOCAL_DB_NAME")
else:
    user = os.getenv("NEON_DB_USER")
    pwd = os.getenv("NEON_DB_PASSWORD")
    host = os.getenv("NEON_DB_HOST")
    port = os.getenv("NEON_DB_PORT", "5432")
    name = os.getenv("NEON_DB_NAME")

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