# MedCase Pro Platform - Rivojlanish Sxemalari
# Urinish, statistika va rivojlanish sxemalari

from pydantic import Field
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime, date

from sxemalar.asosiy import AsosiySchema, IDliSchema, VaqtBelgilariSchema


# ============== Urinish ==============

class UrinishYaratish(AsosiySchema):
    """Urinish yaratish (javob berish)."""
    holat_id: UUID = Field(..., description="Holat ID")
    tanlangan_javob: str = Field(..., max_length=1, description="Tanlangan javob")
    sarflangan_vaqt: int = Field(..., ge=0, description="Sarflangan vaqt (soniyalarda)")
    sessiya_id: Optional[UUID] = Field(None, description="O'qish sessiyasi ID")


class UrinishJavob(IDliSchema, VaqtBelgilariSchema):
    """Urinish javobi."""
    foydalanuvchi_id: UUID
    holat_id: UUID
    sessiya_id: Optional[UUID] = None
    tanlangan_javob: str
    togri: bool
    togri_javob: Optional[str] = None  # FIX: Frontendga to'g'ri javobni yuborish
    sarflangan_vaqt: int
    boshlangan_vaqt: datetime
    tugallangan_vaqt: datetime
    olingan_ball: int
    korib_chiqilgan: bool = False
    korib_chiqish_vaqti: Optional[datetime] = None
    yangi_nishonlar: List[str] = []  # Yangi qo'lga kiritilgan nishonlar


class UrinishToliq(UrinishJavob):
    """Urinish to'liq javobi (holat ma'lumotlari bilan)."""
    holat_sarlavhasi: str
    holat_qiyinligi: str
    togri_javob: str


class UrinishlarRoyxati(AsosiySchema):
    """Urinishlar ro'yxati."""
    urinishlar: List[UrinishJavob] = []
    jami: int = 0
    sahifa: int = 1
    hajm: int = 20


# ============== Sessiya ==============

class SessiyaBoshlash(AsosiySchema):
    """O'qish sessiyasini boshlash."""
    qurilma_turi: Optional[str] = Field(None, max_length=50)


class SessiyaJavob(IDliSchema):
    """Sessiya javobi."""
    foydalanuvchi_id: UUID
    boshlangan_vaqt: datetime
    tugallangan_vaqt: Optional[datetime] = None
    davomiylik: int = 0
    yechilgan_holatlar: int = 0
    togri_javoblar: int = 0
    olingan_ball: int = 0
    faol: bool = True
    qurilma_turi: Optional[str] = None


# ============== Kunlik Statistika ==============

class KunlikStatistikaJavob(IDliSchema):
    """Kunlik statistika javobi."""
    foydalanuvchi_id: UUID
    sana: date
    yechilgan_holatlar: int = 0
    togri_javoblar: int = 0
    notogri_javoblar: int = 0
    jami_vaqt: int = 0
    sessiyalar_soni: int = 0
    olingan_ball: int = 0
    oson_yechilgan: int = 0
    ortacha_yechilgan: int = 0
    qiyin_yechilgan: int = 0

    @property
    def aniqlik_foizi(self) -> float:
        if self.yechilgan_holatlar == 0:
            return 0.0
        return (self.togri_javoblar / self.yechilgan_holatlar) * 100


class HaftalikStatistika(AsosiySchema):
    """Haftalik statistika."""
    kunlar: List[KunlikStatistikaJavob] = []
    jami_holatlar: int = 0
    jami_togri: int = 0
    jami_vaqt: int = 0
    ortacha_aniqlik: float = 0.0


# ============== Umumiy Rivojlanish ==============

class RivojlanishJavob(IDliSchema):
    """Foydalanuvchi rivojlanishi javobi."""
    foydalanuvchi_id: UUID
    jami_urinishlar: int = 0
    togri_javoblar: int = 0
    notogri_javoblar: int = 0
    aniqlik_foizi: float = 0.0
    jami_vaqt: int = 0
    ortacha_vaqt: float = 0.0
    joriy_streak: int = 0
    eng_uzun_streak: int = 0
    oxirgi_faollik: Optional[date] = None
    daraja: int = 1
    jami_ball: int = 0
    oson_yechilgan: int = 0
    oson_togri: int = 0
    ortacha_yechilgan: int = 0
    ortacha_togri: int = 0
    qiyin_yechilgan: int = 0
    qiyin_togri: int = 0
    kategoriya_statistikasi: Dict[str, Any] = {}
    kuchli_tomonlar: List[str] = []
    zaif_tomonlar: List[str] = []


class BolimRivojlanishiJavob(IDliSchema):
    """Bo'lim rivojlanishi javobi."""
    foydalanuvchi_id: UUID
    bolim_id: UUID
    bolim_nomi: Optional[str] = None
    jami_holatlar: int = 0
    yechilgan_holatlar: int = 0
    togri_javoblar: int = 0
    aniqlik_foizi: float = 0.0
    jami_vaqt: int = 0
    tugallangan: bool = False
    tugallangan_vaqt: Optional[datetime] = None

    @property
    def tugallash_foizi(self) -> float:
        if self.jami_holatlar == 0:
            return 0.0
        return (self.yechilgan_holatlar / self.jami_holatlar) * 100


# ============== Statistika ==============

class StatistikaJavob(AsosiySchema):
    """Umumiy statistika javobi."""
    rivojlanish: RivojlanishJavob
    kunlik: KunlikStatistikaJavob
    haftalik: HaftalikStatistika
    bolimlar: List[BolimRivojlanishiJavob] = []


class DashboardStatistika(AsosiySchema):
    """Dashboard uchun statistika."""
    # Asosiy ko'rsatkichlar
    jami_holatlar: int = 0
    aniqlik_foizi: float = 0.0
    bu_hafta_vaqt: int = 0  # daqiqalarda
    daraja: int = 1
    jami_yechilgan_holatlar: int = 0
    ortacha_aniqlik: float = 0.0
    eng_kop_yechilgan_kategoriya: Optional[str] = None
    eng_kam_yechilgan_kategoriya: Optional[str] = None

    # Streak
    joriy_streak: int = 0

    # Kunlik maqsad
    bugungi_holatlar: int = 0
    kunlik_maqsad: int = 10

    # Oxirgi faollik
    oxirgi_urinishlar: List[UrinishJavob] = []

    # Tavsiyalar
    tavsiya_etilgan_bolimlar: List[str] = []


class AnalitikaSorov(AsosiySchema):
    """Analitika so'rovi."""
    boshlash_sanasi: Optional[date] = None
    tugash_sanasi: Optional[date] = None
    kategoriya_id: Optional[UUID] = None
    bolim_id: Optional[UUID] = None
