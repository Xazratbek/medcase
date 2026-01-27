# MedCase Pro Platform - Imtihon Sxemalari
# Timer rejimi va imtihon simulyatsiyasi

from pydantic import Field, field_validator
from typing import Optional, List
from uuid import UUID
from datetime import datetime

from sxemalar.asosiy import AsosiySchema, IDliSchema, VaqtBelgilariSchema
from modellar.imtihon import ImtihonTuri, ImtihonHolati


class ImtihonShabloniYaratish(AsosiySchema):
    """Imtihon shabloni yaratish."""
    nom: str = Field(..., min_length=2, max_length=255, description="Shablon nomi")
    tavsif: Optional[str] = Field(None, description="Tavsif")
    turi: ImtihonTuri = Field(default=ImtihonTuri.VAQTLI, description="Imtihon turi")
    savollar_soni: int = Field(default=50, ge=5, le=200, description="Savollar soni")
    umumiy_vaqt: int = Field(default=3600, ge=300, description="Umumiy vaqt (soniyalarda)")
    savol_vaqti: int = Field(default=90, ge=30, description="Har bir savol uchun vaqt")
    oson_foiz: int = Field(default=30, ge=0, le=100, description="Oson savollar foizi")
    ortacha_foiz: int = Field(default=50, ge=0, le=100, description="O'rtacha savollar foizi")
    qiyin_foiz: int = Field(default=20, ge=0, le=100, description="Qiyin savollar foizi")
    kategoriya_idlari: Optional[List[UUID]] = Field(None, description="Kategoriya filtri")
    bolim_idlari: Optional[List[UUID]] = Field(None, description="Bo'lim filtri")
    aralashtirish: bool = Field(default=True, description="Savollarni aralashtirish")
    javob_aralashtirish: bool = Field(default=True, description="Javoblarni aralashtirish")
    orqaga_qaytish: bool = Field(default=True, description="Orqaga qaytish imkoniyati")
    natijani_korsatish: bool = Field(default=True, description="Natijani ko'rsatish")
    otish_balli: int = Field(default=60, ge=0, le=100, description="O'tish balli")
    
    @field_validator("oson_foiz", "ortacha_foiz", "qiyin_foiz")
    @classmethod
    def foiz_tekshirish(cls, v: int) -> int:
        if not 0 <= v <= 100:
            raise ValueError("Foiz 0 dan 100 gacha bo'lishi kerak")
        return v


class ImtihonShabloniJavob(IDliSchema, VaqtBelgilariSchema):
    """Imtihon shabloni javobi."""
    nom: str
    tavsif: Optional[str] = None
    turi: ImtihonTuri
    savollar_soni: int
    umumiy_vaqt: int
    savol_vaqti: int
    oson_foiz: int
    ortacha_foiz: int
    qiyin_foiz: int
    kategoriya_idlari: Optional[List[UUID]] = None
    bolim_idlari: Optional[List[UUID]] = None
    aralashtirish: bool
    javob_aralashtirish: bool
    orqaga_qaytish: bool
    natijani_korsatish: bool
    otish_balli: int
    otkazilgan_soni: int = 0
    ortacha_ball: int = 0


class ImtihonBoshlash(AsosiySchema):
    """Imtihon boshlash."""
    shablon_id: Optional[UUID] = Field(None, description="Shablon ID (ixtiyoriy)")
    nom: Optional[str] = Field(None, description="Imtihon nomi")
    turi: ImtihonTuri = Field(default=ImtihonTuri.VAQTLI, description="Imtihon turi")
    savollar_soni: int = Field(default=20, ge=5, le=100, description="Savollar soni")
    umumiy_vaqt: int = Field(default=1800, ge=300, description="Umumiy vaqt (soniyalarda)")
    savol_vaqti: int = Field(default=90, ge=30, description="Har bir savol uchun vaqt")
    kategoriya_idlari: Optional[List[UUID]] = None
    bolim_idlari: Optional[List[UUID]] = None
    aralashtirish: bool = True
    orqaga_qaytish: bool = True


class ImtihonSavolJavob(AsosiySchema):
    """Imtihon savoli uchun javob."""
    savol_indeksi: int = Field(..., ge=0, description="Savol indeksi")
    tanlangan_javob: Optional[str] = Field(None, pattern="^[A-Da-d]$", description="Tanlangan javob")
    belgilangan: bool = Field(default=False, description="Keyinroq ko'rish uchun belgilash")
    otkazish: bool = Field(default=False, description="O'tkazib yuborish")


class ImtihonSavoli(AsosiySchema):
    """Imtihon savoli (holat ma'lumotlari)."""
    savol_indeksi: int
    holat_id: UUID
    sarlavha: str
    klinik_stsenariy: str
    savol: str
    variantlar: List[dict]  # [{belgi, matn}]
    qiyinlik: str
    media: List[dict] = []
    qolgan_vaqt: Optional[int] = None  # IMTIHON rejim uchun
    belgilangan: bool = False
    javob_berilgan: bool = False
    tanlangan_javob: Optional[str] = None


class ImtihonHolatiJavob(IDliSchema):
    """Imtihon holati javobi."""
    foydalanuvchi_id: UUID
    nom: str
    turi: ImtihonTuri
    holat: ImtihonHolati
    umumiy_vaqt: int
    savol_vaqti: int
    qolgan_vaqt: Optional[int] = None
    boshlangan_vaqt: Optional[datetime] = None
    jami_savollar: int
    joriy_savol_indeksi: int
    javob_berilgan: int
    togri_javoblar: int
    notogri_javoblar: int
    otkazilgan_savollar: int
    orqaga_qaytish: bool
    aralashtirish: bool


class ImtihonJavobi(IDliSchema):
    """Bitta savol uchun javob ma'lumotlari."""
    imtihon_id: UUID
    holat_id: UUID
    savol_indeksi: int
    tanlangan_javob: Optional[str] = None
    togri_javob: str
    togri: Optional[bool] = None
    sarflangan_vaqt: Optional[int] = None
    otkazilgan: bool = False
    belgilangan: bool = False


class ImtihonNatijasi(IDliSchema, VaqtBelgilariSchema):
    """Imtihon natijasi."""
    foydalanuvchi_id: UUID
    nom: str
    turi: ImtihonTuri
    holat: ImtihonHolati
    boshlangan_vaqt: Optional[datetime] = None
    tugallangan_vaqt: Optional[datetime] = None
    sarflangan_vaqt: int = 0
    jami_savollar: int
    javob_berilgan: int
    togri_javoblar: int
    notogri_javoblar: int
    otkazilgan_savollar: int
    ball_foizi: Optional[int] = None
    otish_balli: int
    otgan: Optional[bool] = None
    javoblar: List[ImtihonJavobi] = []


class ImtihonlarRoyxati(AsosiySchema):
    """Imtihonlar ro'yxati."""
    imtihonlar: List[ImtihonNatijasi] = []
    jami: int = 0
    sahifa: int = 1
    hajm: int = 20
    sahifalar_soni: int = 0


class ImtihonStatistikasi(AsosiySchema):
    """Imtihon statistikasi."""
    jami_imtihonlar: int = 0
    tugallangan_imtihonlar: int = 0
    otgan_imtihonlar: int = 0
    otmagan_imtihonlar: int = 0
    ortacha_ball: float = 0.0
    eng_yuqori_ball: int = 0
    eng_past_ball: int = 0
    jami_sarflangan_vaqt: int = 0  # Soniyalarda
