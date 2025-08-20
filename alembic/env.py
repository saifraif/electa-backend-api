from __future__ import annotations

import os
import sys
from pathlib import Path
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

# -------------------------------------------------------------------
# Ensure project root is on sys.path so "import app...." works
# This file lives at <project_root>/alembic/env.py
# -------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

# -------------------------------------------------------------------
# Import your SQLAlchemy Base (declarative base) and models
# -------------------------------------------------------------------
from app.db.session import Base  # Declarative base where your models inherit

# Import all modules that declare models so Alembic can discover them.
# If a module doesn't exist in your tree, it's safely skipped.
def _import_models() -> None:
    maybes = [
        "app.models.admin",
        "app.models.citizen",
        "app.models.candidate",
        "app.models.user",
        "app.models.__init__",  # in case you re-export there
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
    Prefer DATABASE_URL from environment (e.g., exported from your .env),
    otherwise fall back to sqlalchemy.url in alembic.ini.
    """
    env_url = os.getenv("DATABASE_URL")
    if env_url:
        return env_url
    return config.get_main_option("sqlalchemy.url")


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
