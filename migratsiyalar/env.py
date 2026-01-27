# MedCase Pro Platform - Alembic Muhit Konfiguratsiyasi

import asyncio
import re
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

# Sozlamalar va modellarni import qilish
import sys
sys.path.insert(0, ".")

from sozlamalar.sozlamalar import sozlamalar
from sozlamalar.malumotlar_bazasi import Base

# Barcha modellarni import qilish (metadata uchun)
from modellar.foydalanuvchi import *
from modellar.kategoriya import *
from modellar.holat import *
from modellar.rivojlanish import *
from modellar.gamifikatsiya import *
from modellar.xatcho import *
from modellar.obuna import *
from modellar.bildirishnoma import *
from modellar.izoh import *
from modellar.takrorlash import *
from modellar.imtihon import *

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

def _db_url_tozalash(url: str) -> str:
    """URL dan asyncpg uchun mos bo'lmagan parametrlarni olib tashlaydi."""
    # sslmode va channel_binding ni olib tashlash
    url = re.sub(r'[?&]sslmode=[^&]*', '', url)
    url = re.sub(r'[?&]channel_binding=[^&]*', '', url)
    url = url.replace('?&', '?').rstrip('?')
    return url

def get_url():
    return _db_url_tozalash(sozlamalar.malumotlar_bazasi_url)


def run_migrations_offline() -> None:
    """Offline rejimda migratsiya."""
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Async rejimda migratsiya."""
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = get_url()
    
    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Online rejimda migratsiya."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
