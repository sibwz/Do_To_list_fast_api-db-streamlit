from logging.config import fileConfig
from sqlalchemy import create_engine, pool
from alembic import context
import os
import sys

# ✅ Add project path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# ✅ Import models and DB URL
from app.models import Base


config = context.config
fileConfig(config.config_file_name)
DATABASE_URL = "postgresql+psycopg2://postgres:iq123%40Re@localhost:5432/todo"

# ✅ Not needed anymore, since we’ll use create_engine directly
# config.set_main_option("sqlalchemy.url", DATABASE_URL)

target_metadata = Base.metadata

def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    context.configure(
        url=DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    """Run migrations in 'online' mode."""
    connectable = create_engine(
        DATABASE_URL,
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
