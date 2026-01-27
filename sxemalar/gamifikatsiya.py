# MedCase Pro Platform - Gamifikatsiya Sxemalari
# Nishonlar, ballar va reyting sxemalari

from pydantic import Field
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime

from sxemalar.asosiy import AsosiySchema, IDliSchema, VaqtBelgilariSchema
from modellar.gamifikatsiya import NishonTuri, NishonNodirligi


# ============== Nishon ==============

class NishonYaratish(AsosiySchema):
    """Nishon yaratish."""
    nom: str = Field(..., min_length=2, max_length=100, description="Nishon nomi")
    kod: str = Field(..., min_length=2, max_length=50, description="Nishon kodi")
    tavsif: str = Field(..., min_length=10, description="Tavsif")
    turi: NishonTuri = Field(..., description="Nishon turi")
    nodirlik: NishonNodirligi = Field(default=NishonNodirligi.ODDIY)
    ikonka_url: Optional[str] = Field(None, max_length=500)
    rang: str = Field(default="#FFD700", max_length=7)
    ball_qiymati: int = Field(default=100, ge=1)
    ochish_shartlari: Dict[str, Any] = Field(..., description="Ochish shartlari")


class NishonJavob(IDliSchema, VaqtBelgilariSchema):
    """Nishon javobi."""
    nom: str
    kod: str
    tavsif: str
    turi: NishonTuri
    nodirlik: NishonNodirligi
    ikonka_url: Optional[str] = None
    rang: str
    ball_qiymati: int
    ochish_shartlari: Dict[str, Any]
    ega_bolganlar_soni: int = 0
    faol: bool = True


class FoydalanuvchiNishoniJavob(IDliSchema):
    """Foydalanuvchi nishoni javobi."""
    foydalanuvchi_id: UUID
    nishon_id: UUID
    nishon: NishonJavob
    qolga_kiritilgan_vaqt: datetime
    profilda_korsatish: bool = True


class NishonlarRoyxati(AsosiySchema):
    """Nishonlar ro'yxati."""
    barcha_nishonlar: List[NishonJavob] = []
    qolga_kiritilgan: List[FoydalanuvchiNishoniJavob] = []
    qolga_kiritilmagan: List[NishonJavob] = []


# ============== Ball ==============

class BallJavob(IDliSchema, VaqtBelgilariSchema):
    """Ball javobi."""
    foydalanuvchi_id: UUID
    miqdor: int
    sabab: str
    tavsif: Optional[str] = None
    holat_id: Optional[UUID] = None
    nishon_id: Optional[UUID] = None


class BalllarRoyxati(AsosiySchema):
    """Ballar ro'yxati."""
    ballar: List[BallJavob] = []
    jami_ball: int = 0
    sahifa: int = 1
    hajm: int = 20


class BallQoshish(AsosiySchema):
    """Ball qo'shish (admin uchun)."""
    foydalanuvchi_id: UUID
    miqdor: int = Field(..., description="Ball miqdori")
    sabab: str = Field(..., max_length=100)
    tavsif: Optional[str] = Field(None, max_length=255)


# ============== Reyting ==============

class ReytingJavob(IDliSchema):
    """Reyting javobi."""
    foydalanuvchi_id: UUID
    foydalanuvchi_nomi: Optional[str] = None
    avatar_url: Optional[str] = None
    turi: str
    kategoriya_id: Optional[UUID] = None
    orni: int
    ball: int
    holatlar_soni: int
    aniqlik: float
    davr_boshlanishi: Optional[datetime] = None
    davr_tugashi: Optional[datetime] = None


class ReytingRoyxati(AsosiySchema):
    """Reyting ro'yxati."""
    foydalanuvchilar: List[ReytingJavob] = []
    joriy_foydalanuvchi_orni: Optional[int] = None
    jami: int = 0


class ReytingSorov(AsosiySchema):
    """Reyting so'rovi."""
    turi: str = Field(default="global", description="Reyting turi")
    kategoriya_id: Optional[UUID] = None
    davr: str = Field(default="barcha", description="Davr (haftalik/oylik/barcha)")
    sahifa: int = Field(default=1, ge=1)
    hajm: int = Field(default=50, ge=1, le=100)


# ============== Daraja ==============

class DarajaJavob(IDliSchema):
    """Daraja javobi."""
    daraja: int
    nom: str
    kerakli_ball: int
    ikonka_url: Optional[str] = None
    rang: str
    imkoniyatlar: Dict[str, Any] = {}


class DarajaRivojlanishi(AsosiySchema):
    """Daraja rivojlanishi."""
    joriy_daraja: DarajaJavob
    keyingi_daraja: Optional[DarajaJavob] = None
    joriy_ball: int = 0
    keyingi_darajaga_ball: int = 0
    rivojlanish_foizi: float = 0.0


# ============== Yutuq bildirish ==============

class YangiYutuq(AsosiySchema):
    """Yangi yutuq (nishon yoki daraja)."""
    turi: str = Field(..., description="yutuq turi (nishon/daraja)")
    nishon: Optional[NishonJavob] = None
    daraja: Optional[DarajaJavob] = None
    ball: int = 0
    xabar: str = ""
