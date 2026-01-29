# MedCase Pro Platform - Holat Sxemalari
# Klinik holatlar, variantlar va media sxemalari

from pydantic import Field, field_validator
from typing import Optional, List
from uuid import UUID
from datetime import datetime
import re

from sxemalar.asosiy import AsosiySchema, IDliSchema, VaqtBelgilariSchema
from modellar.holat import HolatTuri, QiyinlikDarajasi, MediaTuri


def _normalize_qiyinlik_value(value):
    """Qiyinlik qiymatini turli yozilishlardan enumga normallashtirish."""
    if value is None:
        return value
    if isinstance(value, QiyinlikDarajasi):
        return value
    text = str(value).strip().lower()
    key = re.sub(r"[^a-z]", "", text)
    if key in {"oson", "basic", "easy"}:
        return QiyinlikDarajasi.OSON
    if key in {"ortacha", "orta", "intermediate", "medium"}:
        return QiyinlikDarajasi.ORTACHA
    if key in {"qiyin", "advanced", "hard"}:
        return QiyinlikDarajasi.QIYIN
    return value


# ============== Variant ==============

class VariantYaratish(AsosiySchema):
    """Variant yaratish."""
    belgi: str = Field(..., max_length=1, description="Variant belgisi (A, B, C, D)")
    matn: str = Field(..., min_length=1, description="Variant matni")
    tushuntirish: Optional[str] = Field(None, description="Tushuntirish")
    togri: bool = Field(default=False, description="To'g'ri variant")
    
    @field_validator("belgi")
    @classmethod
    def belgi_tekshirish(cls, v: str) -> str:
        if v.upper() not in ["A", "B", "C", "D"]:
            raise ValueError("Belgi A, B, C yoki D bo'lishi kerak")
        return v.upper()


class VariantJavob(IDliSchema):
    """Variant javobi."""
    holat_id: UUID
    belgi: str
    matn: str
    tushuntirish: Optional[str] = None
    togri: bool = False


# ============== Media ==============

class MediaYaratish(AsosiySchema):
    """Media yaratish."""
    turi: MediaTuri = Field(..., description="Media turi")
    url: str = Field(..., max_length=500, description="Media URL")
    nom: Optional[str] = Field(None, max_length=255, description="Media nomi")
    tavsif: Optional[str] = Field(None, description="Media tavsifi")
    tartib: int = Field(default=0, ge=0, description="Tartib")
    cloudinary_id: Optional[str] = Field(None, max_length=255)
    fayl_hajmi: Optional[int] = Field(None, ge=0)
    kenglik: Optional[int] = Field(None, ge=0)
    balandlik: Optional[int] = Field(None, ge=0)
    davomiylik: Optional[int] = Field(None, ge=0)


class MediaJavob(IDliSchema):
    """Media javobi."""
    holat_id: UUID
    turi: MediaTuri
    url: str
    nom: Optional[str] = None
    tavsif: Optional[str] = None
    tartib: int = 0
    cloudinary_id: Optional[str] = None
    fayl_hajmi: Optional[int] = None
    kenglik: Optional[int] = None
    balandlik: Optional[int] = None
    davomiylik: Optional[int] = None


# ============== Teg ==============

class TegYaratish(AsosiySchema):
    """Teg yaratish."""
    nom: str = Field(..., min_length=2, max_length=100, description="Teg nomi")
    slug: str = Field(..., min_length=2, max_length=100, description="Teg slug")
    rang: str = Field(default="#6B7280", max_length=7, description="Teg rangi")


class TegJavob(IDliSchema):
    """Teg javobi."""
    nom: str
    slug: str
    rang: str


# ============== Holat ==============

class HolatYaratish(AsosiySchema):
    """Holat yaratish."""
    bolim_id: UUID = Field(..., description="Bo'lim ID")
    sarlavha: str = Field(..., min_length=5, max_length=500, description="Sarlavha")
    klinik_stsenariy: str = Field(..., min_length=50, description="Klinik stsenariy")
    savol: str = Field(..., min_length=10, description="Savol")
    togri_javob: str = Field(..., max_length=1, description="To'g'ri javob (A, B, C, D)")
    umumiy_tushuntirish: Optional[str] = Field(None, description="Umumiy tushuntirish")
    turi: HolatTuri = Field(default=HolatTuri.MCQ, description="Holat turi")
    qiyinlik: QiyinlikDarajasi = Field(default=QiyinlikDarajasi.ORTACHA)
    klinik_kontekst: Optional[str] = Field(None, description="Klinik kontekst")
    ball: int = Field(default=10, ge=1, le=100, description="Ball")
    tavsiya_vaqt: int = Field(default=120, ge=30, le=600, description="Tavsiya vaqt (soniya)")
    variantlar: List[VariantYaratish] = Field(..., min_length=4, max_length=4)
    media: List[MediaYaratish] = Field(default=[], description="Media fayllari")
    teg_idlari: List[UUID] = Field(default=[], description="Teg IDlari")
    chop_etilgan: bool = Field(default=False, description="Chop etilgan")
    
    @field_validator("togri_javob")
    @classmethod
    def togri_javob_tekshirish(cls, v: str) -> str:
        if v.upper() not in ["A", "B", "C", "D"]:
            raise ValueError("To'g'ri javob A, B, C yoki D bo'lishi kerak")
        return v.upper()

    @field_validator("qiyinlik", mode="before")
    @classmethod
    def qiyinlik_normallashtirish(cls, v):
        return _normalize_qiyinlik_value(v)
    
    @field_validator("variantlar")
    @classmethod
    def variantlar_tekshirish(cls, v: List[VariantYaratish]) -> List[VariantYaratish]:
        belgilar = [var.belgi for var in v]
        if sorted(belgilar) != ["A", "B", "C", "D"]:
            raise ValueError("Variantlar A, B, C, D bo'lishi kerak")
        togri_soni = sum(1 for var in v if var.togri)
        if togri_soni != 1:
            raise ValueError("Faqat bitta to'g'ri variant bo'lishi kerak")
        return v


class HolatYangilash(AsosiySchema):
    """Holat yangilash."""
    sarlavha: Optional[str] = Field(None, min_length=5, max_length=500)
    klinik_stsenariy: Optional[str] = Field(None, min_length=50)
    savol: Optional[str] = Field(None, min_length=10)
    togri_javob: Optional[str] = Field(None, max_length=1)
    umumiy_tushuntirish: Optional[str] = None
    turi: Optional[HolatTuri] = None
    qiyinlik: Optional[QiyinlikDarajasi] = None
    klinik_kontekst: Optional[str] = None
    ball: Optional[int] = Field(None, ge=1, le=100)
    tavsiya_vaqt: Optional[int] = Field(None, ge=30, le=600)
    chop_etilgan: Optional[bool] = None
    tekshirilgan: Optional[bool] = None
    faol: Optional[bool] = None

    @field_validator("qiyinlik", mode="before")
    @classmethod
    def qiyinlik_normallashtirish(cls, v):
        return _normalize_qiyinlik_value(v)


class HolatJavob(IDliSchema, VaqtBelgilariSchema):
    """Holat javobi."""
    bolim_id: UUID
    sarlavha: str
    klinik_stsenariy: str
    savol: str
    turi: HolatTuri
    qiyinlik: QiyinlikDarajasi
    klinik_kontekst: Optional[str] = None
    ball: int
    tavsiya_vaqt: int
    urinishlar_soni: int = 0
    togri_javoblar: int = 0
    chop_etilgan: bool = False
    tekshirilgan: bool = False
    faol: bool = True
    variantlar: List[VariantJavob] = []
    media: List[MediaJavob] = []
    teglar: List[TegJavob] = []
    # Kategoriya ma'lumotlari (denormalizatsiya)
    bolim_nomi: Optional[str] = None
    kichik_kategoriya_nomi: Optional[str] = None
    asosiy_kategoriya_nomi: Optional[str] = None


class HolatToliqJavob(HolatJavob):
    """Holat to'liq javobi (javoblar bilan)."""
    togri_javob: str
    umumiy_tushuntirish: Optional[str] = None


class HolatRoyxati(AsosiySchema):
    """Holat ro'yxati (sahifalangan)."""
    holatlar: List[HolatJavob] = []
    jami: int = 0
    sahifa: int = 1
    hajm: int = 20
    sahifalar_soni: int = 0


# ============== Qidiruv ==============

class HolatQidirish(AsosiySchema):
    """Holat qidirish parametrlari."""
    qidiruv: Optional[str] = Field(None, max_length=255, description="Qidiruv so'zi")
    asosiy_kategoriya_id: Optional[UUID] = None
    kichik_kategoriya_id: Optional[UUID] = None
    bolim_id: Optional[UUID] = None
    turi: Optional[HolatTuri] = None
    qiyinlik: Optional[QiyinlikDarajasi] = None
    teg_idlari: List[UUID] = Field(default=[], description="Teg IDlari")
    chop_etilgan: Optional[bool] = None
    yechilgan: Optional[bool] = Field(None, description="Foydalanuvchi yechgan/yechmagan")
    togri_yechilgan: Optional[bool] = Field(None, description="To'g'ri/noto'g'ri yechilgan")
    sahifa: int = Field(default=1, ge=1)
    hajm: int = Field(default=20, ge=1, le=100)
    saralash: str = Field(default="yaratilgan_vaqt", description="Saralash maydoni")
    tartib: str = Field(default="desc", description="Tartib (asc/desc)")

    @field_validator("qiyinlik", mode="before")
    @classmethod
    def qiyinlik_normallashtirish(cls, v):
        return _normalize_qiyinlik_value(v)
