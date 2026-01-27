# MedCase Pro Platform - Takrorlash (Spaced Repetition) Sxemalari
# SM-2 algoritmi uchun Pydantic sxemalari

from pydantic import Field, field_validator
from typing import Optional, List
from uuid import UUID
from datetime import datetime, date

from sxemalar.asosiy import AsosiySchema, IDliSchema, VaqtBelgilariSchema


class TakrorlashKartasiYaratish(AsosiySchema):
    """Takrorlash kartasi yaratish."""
    holat_id: UUID = Field(..., description="Holat ID")


class TakrorlashBaholash(AsosiySchema):
    """
    Takrorlash baholash (SM-2).
    sifat: 0-5 oralig'ida baho
    """
    sifat: int = Field(..., ge=0, le=5, description="Sifat bahosi (0-5)")
    sarflangan_vaqt: Optional[int] = Field(None, ge=0, description="Sarflangan vaqt")
    
    @field_validator("sifat")
    @classmethod
    def sifat_tekshirish(cls, v: int) -> int:
        """
        0 - Umuman eslolmadim
        1 - Noto'g'ri, lekin to'g'ri javobni ko'rganda esladim
        2 - Noto'g'ri, lekin to'g'ri javob juda tanish
        3 - To'g'ri, lekin qiyin bo'ldi
        4 - To'g'ri, biroz o'ylab topdim
        5 - To'g'ri, oson
        """
        if not 0 <= v <= 5:
            raise ValueError("Sifat 0 dan 5 gacha bo'lishi kerak")
        return v


class TakrorlashKartasiJavob(IDliSchema, VaqtBelgilariSchema):
    """Takrorlash kartasi javobi."""
    foydalanuvchi_id: UUID
    holat_id: UUID
    easiness_factor: float
    interval: int
    repetition: int
    oxirgi_takrorlash: Optional[datetime] = None
    keyingi_takrorlash: date
    jami_takrorlashlar: int = 0
    togri_javoblar: int = 0
    oqilgan: bool = False
    aniqlik_foizi: float = 0.0
    
    # Holat ma'lumotlari (qo'shimcha)
    holat_sarlavhasi: Optional[str] = None
    holat_qiyinligi: Optional[str] = None
    kategoriya_nomi: Optional[str] = None


class TakrorlashTarixiJavob(IDliSchema, VaqtBelgilariSchema):
    """Takrorlash tarixi javobi."""
    karta_id: UUID
    sifat: int
    togri: bool
    sarflangan_vaqt: Optional[int] = None
    ef_oldin: Optional[float] = None
    ef_keyin: Optional[float] = None
    interval_oldin: Optional[int] = None
    interval_keyin: Optional[int] = None


class BugungiTakrorlashlar(AsosiySchema):
    """Bugungi takrorlashlar."""
    kartalar: List[TakrorlashKartasiJavob] = []
    jami: int = 0
    yangi: int = 0  # Hali takrorlanmagan
    takrorlash_kerak: int = 0  # Bugun takrorlash kerak
    oqilgan: int = 0  # O'qilgan deb belgilangan


class TakrorlashStatistikasi(AsosiySchema):
    """Takrorlash statistikasi."""
    jami_kartalar: int = 0
    bugun_takrorlash_kerak: int = 0
    ertaga_takrorlash_kerak: int = 0
    hafta_ichida: int = 0
    ortacha_ef: float = 2.5
    jami_takrorlashlar: int = 0
    umumiy_aniqlik: float = 0.0
    streak_kunlar: int = 0  # Ketma-ket takrorlash kunlari


class TakrorlashSessiyasiJavob(IDliSchema):
    """Takrorlash sessiyasi javobi."""
    foydalanuvchi_id: UUID
    boshlangan_vaqt: datetime
    tugallangan_vaqt: Optional[datetime] = None
    jami_kartalar: int = 0
    togri_javoblar: int = 0
    notogri_javoblar: int = 0
    reja_kartalar: int = 20


class TakrorlashSessiyasiBoshlash(AsosiySchema):
    """Takrorlash sessiyasini boshlash."""
    reja_kartalar: int = Field(default=20, ge=1, le=100, description="Rejadagi kartalar soni")
    faqat_bugungi: bool = Field(default=True, description="Faqat bugungi kartalar")
