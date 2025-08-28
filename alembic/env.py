from __future__ import annotations

import sys
from pathlib import Path
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

# -------------------------------------------------------------------
# Ensure project root is on sys.path so "import app...." works
# -------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

# -------------------------------------------------------------------
# Import project settings and SQLAlchemy Base
# -------------------------------------------------------------------
from app.core.config import settings
from app.db.session import Base

# Import all models so Alembic can detect them automatically
def _import_models() -> None:
    maybes = [
        "app.models.citizen",
        "app.models.candidate",
        "app.models.user",
        "app.models.admin",
        "app.models.__init__",  # in case you re-export
    ]
    for mod in maybes:
        try:
            __import__(mod)
        except ModuleNotFoundError:
            pass

_import_models()

# -------------------------------------------------------------------
# Alembic Config
# -------------------------------------------------------------------
config = context.config

# Set up Python logging using alembic.ini
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Metadata for 'autogenerate'
target_metadata = Base.metadata


def get_url() -> str:
    """
    Use the same DB URI as the app (from .env via Settings).
    """
    return settings.sqlalchemy_database_uri


def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode.
    """
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    Run migrations in 'online' mode.
    """
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = get_url()

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        future=True,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
