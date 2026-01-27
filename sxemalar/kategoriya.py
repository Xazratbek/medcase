# MedCase Pro Platform - Kategoriya Sxemalari
# Asosiy kategoriya, kichik kategoriya va bo'lim sxemalari

from pydantic import Field
from typing import Optional, List
from uuid import UUID

from sxemalar.asosiy import AsosiySchema, IDliSchema, VaqtBelgilariSchema


# ============== Asosiy Kategoriya ==============

class AsosiyKategoriyaYaratish(AsosiySchema):
    """Asosiy kategoriya yaratish."""
    nomi: str = Field(..., min_length=2, max_length=255, description="Kategoriya nomi")
    slug: str = Field(..., min_length=2, max_length=255, description="URL slug")
    tavsif: Optional[str] = Field(None, description="Tavsif")
    rasm_url: Optional[str] = Field(None, max_length=500, description="Rasm URL")
    rang: str = Field(default="#3B82F6", max_length=7, description="Rang (HEX)")
    ikonka: Optional[str] = Field(None, max_length=50, description="Ikonka nomi")
    tartib: int = Field(default=0, ge=0, description="Ko'rsatish tartibi")


class AsosiyKategoriyaYangilash(AsosiySchema):
    """Asosiy kategoriya yangilash."""
    nomi: Optional[str] = Field(None, min_length=2, max_length=255)
    slug: Optional[str] = Field(None, min_length=2, max_length=255)
    tavsif: Optional[str] = None
    rasm_url: Optional[str] = Field(None, max_length=500)
    rang: Optional[str] = Field(None, max_length=7)
    ikonka: Optional[str] = Field(None, max_length=50)
    tartib: Optional[int] = Field(None, ge=0)
    faol: Optional[bool] = None


class AsosiyKategoriyaJavob(IDliSchema, VaqtBelgilariSchema):
    """Asosiy kategoriya javobi."""
    nomi: str
    slug: str
    tavsif: Optional[str] = None
    rasm_url: Optional[str] = None
    rang: str
    ikonka: Optional[str] = None
    tartib: int
    holatlar_soni: int = 0
    faol: bool = True


class AsosiyKategoriyaToliq(AsosiyKategoriyaJavob):
    """Asosiy kategoriya to'liq (kichik kategoriyalar bilan)."""
    kichik_kategoriyalar: List["KichikKategoriyaJavob"] = []


# ============== Kichik Kategoriya ==============

class KichikKategoriyaYaratish(AsosiySchema):
    """Kichik kategoriya yaratish."""
    asosiy_kategoriya_id: UUID = Field(..., description="Asosiy kategoriya ID")
    nomi: str = Field(..., min_length=2, max_length=255, description="Nomi")
    slug: str = Field(..., min_length=2, max_length=255, description="URL slug")
    tavsif: Optional[str] = Field(None, description="Tavsif")
    rasm_url: Optional[str] = Field(None, max_length=500)
    rang: str = Field(default="#10B981", max_length=7)
    ikonka: Optional[str] = Field(None, max_length=50)
    tartib: int = Field(default=0, ge=0)


class KichikKategoriyaYangilash(AsosiySchema):
    """Kichik kategoriya yangilash."""
    nomi: Optional[str] = Field(None, min_length=2, max_length=255)
    slug: Optional[str] = Field(None, min_length=2, max_length=255)
    tavsif: Optional[str] = None
    rasm_url: Optional[str] = Field(None, max_length=500)
    rang: Optional[str] = Field(None, max_length=7)
    ikonka: Optional[str] = Field(None, max_length=50)
    tartib: Optional[int] = Field(None, ge=0)
    faol: Optional[bool] = None


class KichikKategoriyaJavob(IDliSchema, VaqtBelgilariSchema):
    """Kichik kategoriya javobi."""
    asosiy_kategoriya_id: UUID
    nomi: str
    slug: str
    tavsif: Optional[str] = None
    rasm_url: Optional[str] = None
    rang: str
    ikonka: Optional[str] = None
    tartib: int
    holatlar_soni: int = 0
    bolimlar_soni: int = 0  # Frontend uchun kerak
    faol: bool = True


class KichikKategoriyaToliq(KichikKategoriyaJavob):
    """Kichik kategoriya to'liq (bo'limlar bilan)."""
    bolimlar: List["BolimJavob"] = []


# ============== Bo'lim ==============

class BolimYaratish(AsosiySchema):
    """Bo'lim yaratish."""
    kichik_kategoriya_id: UUID = Field(..., description="Kichik kategoriya ID")
    nomi: str = Field(..., min_length=2, max_length=255, description="Nomi")
    slug: str = Field(..., min_length=2, max_length=255, description="URL slug")
    tavsif: Optional[str] = Field(None, description="Tavsif")
    rasm_url: Optional[str] = Field(None, max_length=500)
    rang: str = Field(default="#8B5CF6", max_length=7)
    ikonka: Optional[str] = Field(None, max_length=50)
    tartib: int = Field(default=0, ge=0)


class BolimYangilash(AsosiySchema):
    """Bo'lim yangilash."""
    nomi: Optional[str] = Field(None, min_length=2, max_length=255)
    slug: Optional[str] = Field(None, min_length=2, max_length=255)
    tavsif: Optional[str] = None
    rasm_url: Optional[str] = Field(None, max_length=500)
    rang: Optional[str] = Field(None, max_length=7)
    ikonka: Optional[str] = Field(None, max_length=50)
    tartib: Optional[int] = Field(None, ge=0)
    faol: Optional[bool] = None


class BolimJavob(IDliSchema, VaqtBelgilariSchema):
    """Bo'lim javobi."""
    kichik_kategoriya_id: UUID
    nomi: str
    slug: str
    tavsif: Optional[str] = None
    rasm_url: Optional[str] = None
    rang: str
    ikonka: Optional[str] = None
    tartib: int
    holatlar_soni: int = 0
    oson_holatlar: int = 0
    ortacha_holatlar: int = 0
    qiyin_holatlar: int = 0
    faol: bool = True


# ============== Kategoriyalar ro'yxati ==============

class KategoriyalarRoyxati(AsosiySchema):
    """Barcha kategoriyalar ro'yxati."""
    asosiy_kategoriyalar: List[AsosiyKategoriyaToliq] = []
    jami_holatlar: int = 0


# Model yangilash
AsosiyKategoriyaToliq.model_rebuild()
KichikKategoriyaToliq.model_rebuild()
