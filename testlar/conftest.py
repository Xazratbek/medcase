# MedCase Pro Platform - Test Konfiguratsiyasi

import pytest
import asyncio
from typing import AsyncGenerator, Generator
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from ilova.asosiy import ilova
from sozlamalar.malumotlar_bazasi import Base, sessiya_olish

# Test uchun SQLite
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Event loop yaratish."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_engine():
    """Test engine yaratish."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest.fixture
async def test_sessiya(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Test sessiyasi yaratish."""
    sessiya_ishlab_chiqaruvchi = async_sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    async with sessiya_ishlab_chiqaruvchi() as sessiya:
        yield sessiya
        await sessiya.rollback()


@pytest.fixture
async def client(test_sessiya) -> AsyncGenerator[AsyncClient, None]:
    """Test HTTP client yaratish."""
    
    async def override_sessiya():
        yield test_sessiya
    
    ilova.dependency_overrides[sessiya_olish] = override_sessiya
    
    async with AsyncClient(app=ilova, base_url="http://test") as ac:
        yield ac
    
    ilova.dependency_overrides.clear()


@pytest.fixture
async def test_foydalanuvchi(test_sessiya):
    """Test foydalanuvchi yaratish."""
    from modellar.foydalanuvchi import Foydalanuvchi, FoydalanuvchiRoli
    from yordamchilar.xavfsizlik import parol_hashlash
    
    foydalanuvchi = Foydalanuvchi(
        email="test@medcase.uz",
        foydalanuvchi_nomi="testuser",
        parol_hash=parol_hashlash("Test123!"),
        ism="Test",
        familiya="Foydalanuvchi",
        rol=FoydalanuvchiRoli.TALABA,
        email_tasdiqlangan=True
    )
    test_sessiya.add(foydalanuvchi)
    await test_sessiya.commit()
    await test_sessiya.refresh(foydalanuvchi)
    
    return foydalanuvchi


@pytest.fixture
async def auth_token(test_foydalanuvchi):
    """Autentifikatsiya tokeni yaratish."""
    from yordamchilar.xavfsizlik import kirish_tokeni_yaratish
    
    return kirish_tokeni_yaratish(
        str(test_foydalanuvchi.id),
        test_foydalanuvchi.rol.value
    )


@pytest.fixture
async def auth_client(client, auth_token) -> AsyncClient:
    """Autentifikatsiya qilingan client."""
    client.headers["Authorization"] = f"Bearer {auth_token}"
    return client
