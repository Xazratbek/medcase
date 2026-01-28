# MedCase Pro Platform - Ma'lumotlar Bazasi Konfiguratsiyasi
# PostgreSQL bilan async ulanish va sessiya boshqaruvi
# 2K-5K concurrent users uchun optimallashtirilgan

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
    AsyncEngine
)
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import AsyncAdaptedQueuePool
from sqlalchemy import event, text
from typing import AsyncGenerator, Optional
from contextlib import asynccontextmanager
import logging
import ssl
import re

from sozlamalar.sozlamalar import sozlamalar

# Logger sozlash
logger = logging.getLogger(__name__)

# Base model barcha modellar uchun
Base = declarative_base()


class MalumotlarBazasi:
    """
    Ma'lumotlar bazasi ulanishini boshqaruvchi klass.
    2000-5000 bir vaqtda foydalanuvchi uchun optimallashtirilgan.

    Optimizatsiyalar:
    - AsyncAdaptedQueuePool - connection pooling
    - Prepared statements cache
    - Connection recycling
    - Lazy loading disabled
    """

    def __init__(self):
        self._engine: Optional[AsyncEngine] = None
        self._sessiya_ishlab_chiqaruvchi: Optional[async_sessionmaker] = None
        self._ssl_context: Optional[ssl.SSLContext] = None

    def _ssl_kontekst_yaratish(self) -> ssl.SSLContext:
        """SSL kontekstini yaratadi va keshlaydi."""
        if self._ssl_context is None:
            self._ssl_context = ssl.create_default_context()
            self._ssl_context.check_hostname = False
            self._ssl_context.verify_mode = ssl.CERT_NONE
        return self._ssl_context

    def _db_url_tozalash(self, url: str) -> str:
        """URL dan asyncpg uchun mos bo'lmagan parametrlarni olib tashlaydi."""
        # sslmode va channel_binding ni olib tashlash
        url = re.sub(r'[?&]sslmode=[^&]*', '', url)
        url = re.sub(r'[?&]channel_binding=[^&]*', '', url)
        url = url.replace('?&', '?').rstrip('?')
        return url

    def _engine_yaratish(self) -> AsyncEngine:
        """
        Async engine yaratadi yuqori darajada optimallashtirilgan sozlamalar bilan.

        Performance optimizatsiyalari:
        - Connection pool: 10-50 ulanish
        - Statement cache: 1000 ta so'rov
        - Connection recycling: 30 daqiqa
        - Pool pre-ping: o'chirilgan (tezlik uchun)
        """
        db_url = self._db_url_tozalash(sozlamalar.malumotlar_bazasi_url)
        ssl_context = self._ssl_kontekst_yaratish()

        # Ishlab chiqarish vs development sozlamalari
        if sozlamalar.ishlab_chiqarish_muhiti:
            pool_size = 50
            max_overflow = 50
            pool_recycle = 1800  # 30 daqiqa
        else:
            pool_size = 40
            max_overflow = 20
            pool_recycle = 3600  # 1 soat

        engine = create_async_engine(
            db_url,
            # === Connection Pool Sozlamalari ===
            poolclass=AsyncAdaptedQueuePool,
            pool_size=pool_size,
            max_overflow=max_overflow,
            pool_recycle=pool_recycle,
            pool_pre_ping=True,  # FIX: Stale connectionlarni aniqlash uchun yoqildi
            pool_timeout=10,  # 10 soniya kutish

            # === Performance Sozlamalari ===
            echo=False,  # Production'da log o'chirilgan
            echo_pool=False,

            # === Asyncpg Driver Sozlamalari ===
            connect_args={
                "ssl": ssl_context,
                "command_timeout": 30,  # 30 soniya timeout
                "statement_cache_size": 1000,  # So'rovlarni keshlash
                "prepared_statement_cache_size": 500,  # Prepared statements
            },
        )

        return engine

    async def ulanish(self) -> None:
        """
        Ma'lumotlar bazasiga ulanadi va engine yaratadi.
        Pool'ni isitadi (warm up) - birinchi so'rovlar tez bo'lishi uchun.
        """
        if self._engine is None:
            logger.info("Ma'lumotlar bazasiga ulanish boshlanmoqda...")

            self._engine = self._engine_yaratish()

            # Optimallashtirilgan sessiya factory
            self._sessiya_ishlab_chiqaruvchi = async_sessionmaker(
                bind=self._engine,
                class_=AsyncSession,
                expire_on_commit=False,  # Commit'dan keyin ob'ektlarni expire qilmaslik
                autocommit=False,
                autoflush=False,  # Avtomatik flush o'chirilgan - manual control
            )

            # Pool'ni isitish - bir nechta ulanish yaratish
            async with self._engine.begin() as conn:
                await conn.execute(text("SELECT 1"))

            logger.info("Ma'lumotlar bazasiga muvaffaqiyatli ulandi")

    async def uzish(self) -> None:
        """
        Ma'lumotlar bazasi ulanishini yopadi.
        """
        if self._engine is not None:
            logger.info("Ma'lumotlar bazasi ulanishi yopilmoqda...")
            await self._engine.dispose()
            self._engine = None
            self._sessiya_ishlab_chiqaruvchi = None
            logger.info("Ma'lumotlar bazasi ulanishi yopildi")

    @asynccontextmanager
    async def sessiya(self) -> AsyncGenerator[AsyncSession, None]:
        """
        Async context manager sessiya olish uchun.
        Tranzaksiyalarni avtomatik boshqaradi.
        """
        if self._sessiya_ishlab_chiqaruvchi is None:
            await self.ulanish()

        sessiya = self._sessiya_ishlab_chiqaruvchi()
        try:
            yield sessiya
            # Har doim commit - flush() dan keyin new/dirty bo'sh bo'ladi
            await sessiya.commit()
        except Exception as xato:
            await sessiya.rollback()
            logger.error(f"Sessiya xatosi: {xato}")
            raise
        finally:
            await sessiya.close()

    async def jadvallar_yaratish(self) -> None:
        """
        Barcha jadvallarni yaratadi (faqat ishlab chiqish uchun).
        Ishlab chiqarishda Alembic migratsiyalaridan foydalaning.
        """
        if self._engine is None:
            await self.ulanish()

        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        logger.info("Jadvallar muvaffaqiyatli yaratildi")

    async def jadvallar_ochirish(self) -> None:
        """
        Barcha jadvallarni o'chiradi (faqat sinov uchun).
        """
        if self._engine is None:
            await self.ulanish()

        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)

        logger.warning("Barcha jadvallar o'chirildi")

    @property
    def engine(self) -> Optional[AsyncEngine]:
        """Engine ob'ektini qaytaradi."""
        return self._engine

    @property
    def ulangan(self) -> bool:
        """Ulanish holatini tekshiradi."""
        return self._engine is not None


# Global ma'lumotlar bazasi ob'ekti
malumotlar_bazasi = MalumotlarBazasi()


async def sessiya_olish() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI Dependency Injection uchun sessiya olish.
    OPTIMIZED: Minimal overhead

    Foydalanish:
        @router.get("/")
        async def endpoint(db: AsyncSession = Depends(sessiya_olish)):
            ...
    """
    if malumotlar_bazasi._sessiya_ishlab_chiqaruvchi is None:
        await malumotlar_bazasi.ulanish()

    sessiya = malumotlar_bazasi._sessiya_ishlab_chiqaruvchi()
    try:
        yield sessiya
        # Har doim commit qilish - flush() dan keyin new/dirty bo'sh bo'ladi
        # lekin tranzaksiya hali ham ochiq bo'ladi
        await sessiya.commit()
    except Exception:
        await sessiya.rollback()
        raise
    finally:
        await sessiya.close()


async def faqat_oqish_sessiyasi() -> AsyncGenerator[AsyncSession, None]:
    """
    Faqat o'qish uchun optimallashtirilgan sessiya.
    SELECT so'rovlari uchun ishlatiladi - commit kerak emas.
    """
    if malumotlar_bazasi._sessiya_ishlab_chiqaruvchi is None:
        await malumotlar_bazasi.ulanish()

    sessiya = malumotlar_bazasi._sessiya_ishlab_chiqaruvchi()
    try:
        yield sessiya
    finally:
        await sessiya.close()
