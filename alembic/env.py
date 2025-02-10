import asyncio
from logging.config import fileConfig
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlalchemy import pool
from alembic import context

# Alembic konfiguratsiyasi
config = context.config
fileConfig(config.config_file_name)

from models.database import Base  # Barcha modellarni chaqirish
import os
from dotenv import load_dotenv
load_dotenv()

DB_USER=os.getenv("DB_USER")
DB_HOST=os.getenv("DB_HOST")
DB_NAME=os.getenv("DB_NAME")
DB_PASSWORD=os.getenv("DB_PASSWORD")
def get_url():
    return f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"

config.set_main_option("sqlalchemy.url", get_url())
target_metadata = Base.metadata

async def run_migrations():
    """Asinxron migratsiyalarni ishga tushirish"""
    connectable = create_async_engine(
        get_url(),
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)  # ✅ To‘g‘ri usul

    await connectable.dispose()

def do_run_migrations(connection):
    """Migratsiyalarni bajarish"""
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()

if context.is_offline_mode():
    """Offline rejimda ishlash"""
    context.configure(url=get_url(), target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()
else:
    asyncio.run(run_migrations())  # ✅ Asinxron migratsiyalarni ishlatish
