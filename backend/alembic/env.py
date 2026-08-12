import os
import sys
from logging.config import fileConfig

from sqlalchemy import create_engine, pool
from alembic import context

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from db.models import Base

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

# --- DYNAMIC DATABASE URL BUILDER ---
def get_db_url() -> str:
    # Allow explicitly passed DATABASE_URL if present
    if explicit_url := os.getenv("DATABASE_URL"):
        return explicit_url

    env = os.getenv("ENVIRONMENT", "local").lower()

    if env == "local":
        user = os.getenv("POSTGRES_USER", "postgres")
        password = os.getenv("POSTGRES_PASSWORD", "password")
        host = os.getenv("POSTGRES_HOST", "db")
        port = os.getenv("POSTGRES_PORT", "5432")
        db_name = os.getenv("POSTGRES_DB", "volleyball_db")
        return f"postgresql://{user}:{password}@{host}:{port}/{db_name}"
    else:
        user = os.getenv("NEON_DB_USER")
        password = os.getenv("NEON_DB_PASSWORD")
        host = os.getenv("NEON_DB_HOST")
        port = os.getenv("NEON_DB_PORT", "5432")
        db_name = os.getenv("NEON_DB_NAME")
        # Neon PostgreSQL requires SSL
        return f"postgresql://{user}:{password}@{host}:{port}/{db_name}?sslmode=require"

db_url = get_db_url()


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    context.configure(
        url=db_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = create_engine(db_url, poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()