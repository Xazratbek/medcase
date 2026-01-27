# MedCase Pro Platform - Autentifikatsiya Testlari

import pytest
from httpx import AsyncClient


class TestRoyxatdanOtish:
    """Ro'yxatdan o'tish testlari."""
    
    @pytest.mark.asyncio
    async def test_muvaffaqiyatli_royxatdan_otish(self, client: AsyncClient):
        """Muvaffaqiyatli ro'yxatdan o'tish."""
        javob = await client.post(
            "/api/v1/autentifikatsiya/royxatdan-otish",
            json={
                "email": "yangi@medcase.uz",
                "foydalanuvchi_nomi": "yangiuser",
                "parol": "Parol123!",
                "parol_tasdiqlash": "Parol123!",
                "ism": "Yangi",
                "familiya": "Foydalanuvchi"
            }
        )
        
        assert javob.status_code == 201
        malumot = javob.json()
        assert malumot["email"] == "yangi@medcase.uz"
        assert malumot["foydalanuvchi_nomi"] == "yangiuser"
    
    @pytest.mark.asyncio
    async def test_takroriy_email(self, client: AsyncClient, test_foydalanuvchi):
        """Mavjud email bilan ro'yxatdan o'tish."""
        javob = await client.post(
            "/api/v1/autentifikatsiya/royxatdan-otish",
            json={
                "email": test_foydalanuvchi.email,
                "foydalanuvchi_nomi": "boshqauser",
                "parol": "Parol123!",
                "parol_tasdiqlash": "Parol123!",
                "ism": "Boshqa",
                "familiya": "Foydalanuvchi"
            }
        )
        
        assert javob.status_code == 400
    
    @pytest.mark.asyncio
    async def test_zaif_parol(self, client: AsyncClient):
        """Zaif parol bilan ro'yxatdan o'tish."""
        javob = await client.post(
            "/api/v1/autentifikatsiya/royxatdan-otish",
            json={
                "email": "zaif@medcase.uz",
                "foydalanuvchi_nomi": "zaifuser",
                "parol": "123456",
                "parol_tasdiqlash": "123456",
                "ism": "Zaif",
                "familiya": "Parol"
            }
        )
        
        assert javob.status_code == 422


class TestKirish:
    """Kirish testlari."""
    
    @pytest.mark.asyncio
    async def test_muvaffaqiyatli_kirish(self, client: AsyncClient, test_foydalanuvchi):
        """Muvaffaqiyatli kirish."""
        javob = await client.post(
            "/api/v1/autentifikatsiya/kirish",
            json={
                "email_yoki_nom": test_foydalanuvchi.email,
                "parol": "Test123!"
            }
        )
        
        assert javob.status_code == 200
        malumot = javob.json()
        assert "kirish_tokeni" in malumot
        assert "yangilash_tokeni" in malumot
    
    @pytest.mark.asyncio
    async def test_notogri_parol(self, client: AsyncClient, test_foydalanuvchi):
        """Noto'g'ri parol bilan kirish."""
        javob = await client.post(
            "/api/v1/autentifikatsiya/kirish",
            json={
                "email_yoki_nom": test_foydalanuvchi.email,
                "parol": "NotogriParol123!"
            }
        )
        
        assert javob.status_code == 401
    
    @pytest.mark.asyncio
    async def test_mavjud_bolmagan_foydalanuvchi(self, client: AsyncClient):
        """Mavjud bo'lmagan foydalanuvchi bilan kirish."""
        javob = await client.post(
            "/api/v1/autentifikatsiya/kirish",
            json={
                "email_yoki_nom": "yoq@medcase.uz",
                "parol": "Parol123!"
            }
        )
        
        assert javob.status_code == 401


class TestJoriyFoydalanuvchi:
    """Joriy foydalanuvchi testlari."""
    
    @pytest.mark.asyncio
    async def test_men_endpoint(self, auth_client: AsyncClient, test_foydalanuvchi):
        """Joriy foydalanuvchi ma'lumotlari."""
        javob = await auth_client.get("/api/v1/autentifikatsiya/men")
        
        assert javob.status_code == 200
        malumot = javob.json()
        assert malumot["email"] == test_foydalanuvchi.email
    
    @pytest.mark.asyncio
    async def test_autentifikatsiyasiz(self, client: AsyncClient):
        """Autentifikatsiyasiz so'rov."""
        javob = await client.get("/api/v1/autentifikatsiya/men")
        
        assert javob.status_code == 401
