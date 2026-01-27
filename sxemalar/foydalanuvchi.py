# MedCase Pro Platform - Foydalanuvchi Sxemalari
# Ro'yxatdan o'tish, kirish va profil sxemalari

from pydantic import BaseModel, Field, EmailStr, field_validator
from typing import Optional, List
from datetime import datetime
from uuid import UUID
import re

from sxemalar.asosiy import AsosiySchema, VaqtBelgilariSchema, IDliSchema
from modellar.foydalanuvchi import FoydalanuvchiRoli


# ============== Kirish/Ro'yxatdan o'tish ==============

class FoydalanuvchiYaratish(AsosiySchema):
    """Yangi foydalanuvchi yaratish."""
    email: EmailStr = Field(..., description="Email manzil")
    foydalanuvchi_nomi: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="Foydalanuvchi nomi"
    )
    parol: str = Field(
        ...,
        min_length=8,
        max_length=100,
        description="Parol"
    )
    parol_tasdiqlash: str = Field(..., description="Parol tasdiqlash")
    ism: str = Field(..., min_length=2, max_length=100, description="Ism")
    familiya: str = Field(..., min_length=2, max_length=100, description="Familiya")
    rol: FoydalanuvchiRoli = Field(
        default=FoydalanuvchiRoli.TALABA,
        description="Foydalanuvchi roli"
    )
    
    @field_validator("foydalanuvchi_nomi")
    @classmethod
    def foydalanuvchi_nomi_tekshirish(cls, v: str) -> str:
        """Foydalanuvchi nomini tekshirish."""
        if not re.match(r"^[a-zA-Z0-9_]+$", v):
            raise ValueError(
                "Foydalanuvchi nomi faqat harflar, raqamlar va pastki chiziq bo'lishi mumkin"
            )
        return v.lower()
    
    @field_validator("parol")
    @classmethod
    def parol_tekshirish(cls, v: str) -> str:
        """Parol murakkabligini tekshirish."""
        if not re.search(r"[A-Z]", v):
            raise ValueError("Parolda kamida bitta katta harf bo'lishi kerak")
        if not re.search(r"[a-z]", v):
            raise ValueError("Parolda kamida bitta kichik harf bo'lishi kerak")
        if not re.search(r"\d", v):
            raise ValueError("Parolda kamida bitta raqam bo'lishi kerak")
        return v
    
    @field_validator("parol_tasdiqlash")
    @classmethod
    def parollar_mos(cls, v: str, info) -> str:
        """Parollar mosligini tekshirish."""
        if "parol" in info.data and v != info.data["parol"]:
            raise ValueError("Parollar mos emas")
        return v


class FoydalanuvchiKirish(AsosiySchema):
    """Foydalanuvchi kirish."""
    email_yoki_nom: str = Field(..., description="Email yoki foydalanuvchi nomi")
    parol: str = Field(..., description="Parol")
    eslab_qolish: bool = Field(default=False, description="Eslab qolish")


class TokenJavob(AsosiySchema):
    """Token javobi."""
    kirish_tokeni: str = Field(..., description="Kirish tokeni")
    yangilash_tokeni: str = Field(..., description="Yangilash tokeni")
    token_turi: str = Field(default="Bearer", description="Token turi")
    amal_qilish_muddati: int = Field(..., description="Amal qilish muddati (soniyalarda)")


class TokenYangilash(AsosiySchema):
    """Token yangilash."""
    yangilash_tokeni: str = Field(..., description="Yangilash tokeni")


class ParolOzgartirish(AsosiySchema):
    """Parol o'zgartirish."""
    joriy_parol: str = Field(..., description="Joriy parol")
    yangi_parol: str = Field(..., min_length=8, description="Yangi parol")
    yangi_parol_tasdiqlash: str = Field(..., description="Yangi parol tasdiqlash")
    
    @field_validator("yangi_parol_tasdiqlash")
    @classmethod
    def parollar_mos(cls, v: str, info) -> str:
        if "yangi_parol" in info.data and v != info.data["yangi_parol"]:
            raise ValueError("Yangi parollar mos emas")
        return v


class ParolTiklash(AsosiySchema):
    """Parol tiklash so'rovi."""
    email: EmailStr = Field(..., description="Email manzil")


class ParolTiklashTasdiqlash(AsosiySchema):
    """Parol tiklash tasdiqlash."""
    token: str = Field(..., description="Tiklash tokeni")
    yangi_parol: str = Field(..., min_length=8, description="Yangi parol")
    yangi_parol_tasdiqlash: str = Field(..., description="Yangi parol tasdiqlash")


class EmailTasdiqlash(AsosiySchema):
    """Email tasdiqlash."""
    token: str = Field(..., description="Tasdiqlash tokeni")


# ============== Foydalanuvchi javoblari ==============

class FoydalanuvchiJavob(IDliSchema, VaqtBelgilariSchema):
    """Foydalanuvchi javobi."""
    email: str = Field(..., description="Email")
    foydalanuvchi_nomi: str = Field(..., description="Foydalanuvchi nomi")
    ism: str = Field(..., description="Ism")
    familiya: str = Field(..., description="Familiya")
    rol: FoydalanuvchiRoli = Field(..., description="Rol")
    email_tasdiqlangan: bool = Field(..., description="Email tasdiqlangan")
    faol: bool = Field(..., description="Faol holat")
    oxirgi_kirish: Optional[datetime] = Field(None, description="Oxirgi kirish")
    
    @property
    def toliq_ism(self) -> str:
        return f"{self.ism} {self.familiya}"


class FoydalanuvchiYangilash(AsosiySchema):
    """Foydalanuvchi yangilash."""
    ism: Optional[str] = Field(None, min_length=2, max_length=100)
    familiya: Optional[str] = Field(None, min_length=2, max_length=100)
    foydalanuvchi_nomi: Optional[str] = Field(None, min_length=3, max_length=50)


# ============== Profil ==============

class ProfilYangilash(AsosiySchema):
    """Profil yangilash."""
    avatar_url: Optional[str] = Field(None, max_length=500)
    muassasa: Optional[str] = Field(None, max_length=255)
    mutaxassislik: Optional[str] = Field(None, max_length=255)
    kurs_yili: Optional[int] = Field(None, ge=1, le=6)
    bio: Optional[str] = Field(None, max_length=1000)
    telefon: Optional[str] = Field(None, max_length=20)
    shahar: Optional[str] = Field(None, max_length=100)
    mamlakat: Optional[str] = Field(None, max_length=100)
    til: Optional[str] = Field(None, max_length=10)
    mavzu: Optional[str] = Field(None, max_length=20)
    kunlik_maqsad: Optional[int] = Field(None, ge=1, le=100)
    profil_ochiq: Optional[bool] = None
    reytingda_korsatish: Optional[bool] = None


class ProfilJavob(IDliSchema, VaqtBelgilariSchema):
    """Profil javobi."""
    foydalanuvchi_id: UUID = Field(..., description="Foydalanuvchi ID")
    avatar_url: Optional[str] = None
    muassasa: Optional[str] = None
    mutaxassislik: Optional[str] = None
    kurs_yili: Optional[int] = None
    bio: Optional[str] = None
    telefon: Optional[str] = None
    shahar: Optional[str] = None
    mamlakat: Optional[str] = None
    til: str = Field(default="uz")
    mavzu: str = Field(default="yorug")
    kunlik_maqsad: int = Field(default=10)
    profil_ochiq: bool = Field(default=True)
    reytingda_korsatish: bool = Field(default=True)


class FoydalanuvchiToliqJavob(FoydalanuvchiJavob):
    """Foydalanuvchi to'liq javobi (profil bilan)."""
    profil: Optional[ProfilJavob] = None


# ============== OAuth ==============

class OAuthKirish(AsosiySchema):
    """OAuth kirish."""
    provayder: str = Field(..., description="OAuth provayder (google/microsoft)")
    token: str = Field(..., description="OAuth token")


class OAuthCallback(AsosiySchema):
    """OAuth callback."""
    kod: str = Field(..., description="Authorization kod")
    holat: Optional[str] = Field(None, description="State parametr")
