"""Alembic environment — reads DB URL from app.config at runtime."""

from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool

from alembic import context

# Import app config so the DB URL is resolved at runtime (not hard-coded)
from app.config import DATABASE_URL

# Import all models so Alembic can detect schema changes
from app.database import Base  # noqa: F401
import app.models  # noqa: F401 — registers Book + Reservation with Base.metadata

config = context.config

# Override the sqlalchemy.url from alembic.ini with the runtime value
config.set_main_option("sqlalchemy.url", DATABASE_URL)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        render_as_batch=True,  # required for SQLite ALTER TABLE support
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            render_as_batch=True,  # required for SQLite ALTER TABLE support
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
