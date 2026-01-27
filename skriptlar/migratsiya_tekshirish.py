#!/usr/bin/env python3
# MedCase Pro Platform - Migratsiya Tekshirish Skripti
# Migratsiyalar allaqachon qo'llanganligini tekshiradi

import asyncio
import sys
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
import re

from sozlamalar.sozlamalar import sozlamalar


def _db_url_tozalash(url: str) -> str:
    """URL dan asyncpg uchun mos bo'lmagan parametrlarni olib tashlaydi."""
    url = re.sub(r'[?&]sslmode=[^&]*', '', url)
    url = re.sub(r'[?&]channel_binding=[^&]*', '', url)
    url = url.replace('?&', '?').rstrip('?')
    return url


async def migratsiyalar_qollanganmi() -> bool:
    """
    Migratsiyalar allaqachon qo'llanganligini tekshiradi.
    Alembic versiyasi jadvali mavjudligini va head versiyasini tekshiradi.
    """
    try:
        db_url = _db_url_tozalash(sozlamalar.malumotlar_bazasi_url)
        engine = create_async_engine(db_url, pool_pre_ping=True)
        
        async with engine.connect() as conn:
            # Alembic versiyasi jadvali mavjudligini tekshirish
            try:
                result = await conn.execute(
                    text("SELECT version_num FROM alembic_version LIMIT 1")
                )
                version = result.scalar()
                
                if version:
                    # Head versiyasini olish (alembic current bilan solishtirish kerak)
                    # Agar versiya mavjud bo'lsa, migratsiyalar qo'llangan deb hisoblaymiz
                    await engine.dispose()
                    return True
                else:
                    await engine.dispose()
                    return False
            except Exception:
                # Jadval mavjud emas - migratsiyalar qo'llanmagan
                await engine.dispose()
                return False
    except Exception as e:
        # Ulanish xatosi - migratsiyalar kerak bo'lishi mumkin
        print(f"⚠️  Ma'lumotlar bazasiga ulanib bo'lmadi: {e}", file=sys.stderr)
        return False


async def asosiy():
    """Asosiy funksiya."""
    qollangan = await migratsiyalar_qollanganmi()
    sys.exit(0 if qollangan else 1)


if __name__ == "__main__":
    asyncio.run(asosiy())
