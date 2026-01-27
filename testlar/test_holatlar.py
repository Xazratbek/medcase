# MedCase Pro Platform - Holatlar Testlari

import pytest
from httpx import AsyncClient
from uuid import uuid4


class TestHolatlarRoyxati:
    """Holatlar ro'yxati testlari."""
    
    @pytest.mark.asyncio
    async def test_bosh_royxat(self, client: AsyncClient):
        """Bo'sh holatlar ro'yxati."""
        javob = await client.get("/api/v1/holat/")
        
        assert javob.status_code == 200
        malumot = javob.json()
        assert "holatlar" in malumot
        assert "jami" in malumot
    
    @pytest.mark.asyncio
    async def test_sahifalash(self, client: AsyncClient):
        """Sahifalash parametrlari."""
        javob = await client.get("/api/v1/holat/?sahifa=1&hajm=10")
        
        assert javob.status_code == 200
        malumot = javob.json()
        assert malumot["sahifa"] == 1
        assert malumot["hajm"] == 10


class TestTasodifiyHolatlar:
    """Tasodifiy holatlar testlari."""
    
    @pytest.mark.asyncio
    async def test_tasodifiy_olish(self, client: AsyncClient):
        """Tasodifiy holatlar olish."""
        javob = await client.get("/api/v1/holat/tasodifiy?soni=5")
        
        assert javob.status_code == 200
        assert isinstance(javob.json(), list)


class TestTeglar:
    """Teglar testlari."""
    
    @pytest.mark.asyncio
    async def test_teglar_royxati(self, client: AsyncClient):
        """Teglar ro'yxati."""
        javob = await client.get("/api/v1/holat/teglar")
        
        assert javob.status_code == 200
        assert isinstance(javob.json(), list)
