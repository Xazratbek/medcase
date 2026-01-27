# MedCase Pro Platform - Imtihon Simulyatsiyasi Modellari
# Timer rejimi va imtihon simulyatsiyasi

from sqlalchemy import (
    Column, String, Integer, ForeignKey, Text,
    Boolean, DateTime, Index, func, Enum as SQLEnum
)
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship
import enum
from datetime import datetime

from modellar.asosiy import AsosiyModel


class ImtihonTuri(str, enum.Enum):
    """Imtihon turlari."""
    AMALIYOT = "amaliyot"  # Practice mode - vaqt cheksiz
    VAQTLI = "vaqtli"  # Timed mode - umumiy vaqt chegarasi
    IMTIHON = "imtihon"  # Exam mode - har bir savolga vaqt


class ImtihonHolati(str, enum.Enum):
    """Imtihon holatlari."""
    KUTILMOQDA = "kutilmoqda"  # Hali boshlanmagan
    JARAYONDA = "jarayonda"  # O'tkazilmoqda
    TUGALLANGAN = "tugallangan"  # Yakunlangan
    BEKOR_QILINGAN = "bekor_qilingan"  # Bekor qilingan


class ImtihonShabloni(AsosiyModel):
    """
    Imtihon shabloni - qayta ishlatilishi mumkin.
    Admin tomonidan yaratiladi.
    """
    __tablename__ = "imtihon_shablonlari"
    
    # Asosiy ma'lumotlar
    nom = Column(
        String(255),
        nullable=False,
        comment="Shablon nomi"
    )
    tavsif = Column(
        Text,
        nullable=True,
        comment="Shablon tavsifi"
    )
    
    # Konfiguratsiya
    turi = Column(
        SQLEnum(ImtihonTuri),
        default=ImtihonTuri.VAQTLI,
        nullable=False,
        comment="Imtihon turi"
    )
    savollar_soni = Column(
        Integer,
        default=50,
        nullable=False,
        comment="Savollar soni"
    )
    umumiy_vaqt = Column(
        Integer,
        default=3600,
        nullable=False,
        comment="Umumiy vaqt (soniyalarda) - VAQTLI rejim uchun"
    )
    savol_vaqti = Column(
        Integer,
        default=90,
        nullable=False,
        comment="Har bir savol uchun vaqt (soniyalarda) - IMTIHON rejim uchun"
    )
    
    # Qiyinlik tarqatish (foizlarda)
    oson_foiz = Column(Integer, default=30, comment="Oson savollar foizi")
    ortacha_foiz = Column(Integer, default=50, comment="O'rtacha savollar foizi")
    qiyin_foiz = Column(Integer, default=20, comment="Qiyin savollar foizi")
    
    # Filtrlar
    kategoriya_idlari = Column(
        ARRAY(UUID(as_uuid=True)),
        nullable=True,
        comment="Kategoriya filtri"
    )
    bolim_idlari = Column(
        ARRAY(UUID(as_uuid=True)),
        nullable=True,
        comment="Bo'lim filtri"
    )
    
    # Sozlamalar
    aralashtirish = Column(
        Boolean,
        default=True,
        nullable=False,
        comment="Savollarni aralashtirish"
    )
    javob_aralashtirish = Column(
        Boolean,
        default=True,
        nullable=False,
        comment="Javob variantlarini aralashtirish"
    )
    orqaga_qaytish = Column(
        Boolean,
        default=True,
        nullable=False,
        comment="Oldingi savolga qaytish imkoniyati"
    )
    natijani_korsatish = Column(
        Boolean,
        default=True,
        nullable=False,
        comment="Javobdan keyin natijani ko'rsatish"
    )
    
    # O'tish balli
    otish_balli = Column(
        Integer,
        default=60,
        nullable=False,
        comment="O'tish balli (foizda)"
    )
    
    # Statistika
    otkazilgan_soni = Column(
        Integer,
        default=0,
        nullable=False,
        comment="O'tkazilgan imtihonlar soni"
    )
    ortacha_ball = Column(
        Integer,
        default=0,
        nullable=False,
        comment="O'rtacha ball"
    )
    
    # Munosabatlar
    imtihonlar = relationship(
        "Imtihon",
        back_populates="shablon",
        cascade="all, delete-orphan"
    )


class Imtihon(AsosiyModel):
    """
    Foydalanuvchi imtihoni - aktiv sessiya.
    """
    __tablename__ = "imtihonlar"
    
    # Bog'lanishlar
    foydalanuvchi_id = Column(
        UUID(as_uuid=True),
        ForeignKey("foydalanuvchilar.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Foydalanuvchi ID"
    )
    shablon_id = Column(
        UUID(as_uuid=True),
        ForeignKey("imtihon_shablonlari.id", ondelete="SET NULL"),
        nullable=True,
        comment="Shablon ID (agar shablondan yaratilgan bo'lsa)"
    )
    
    # Imtihon ma'lumotlari
    nom = Column(
        String(255),
        nullable=False,
        comment="Imtihon nomi"
    )
    turi = Column(
        SQLEnum(ImtihonTuri),
        default=ImtihonTuri.VAQTLI,
        nullable=False,
        comment="Imtihon turi"
    )
    holat = Column(
        SQLEnum(ImtihonHolati),
        default=ImtihonHolati.KUTILMOQDA,
        nullable=False,
        index=True,
        comment="Imtihon holati"
    )
    
    # Vaqt sozlamalari
    umumiy_vaqt = Column(
        Integer,
        default=3600,
        nullable=False,
        comment="Umumiy vaqt (soniyalarda)"
    )
    savol_vaqti = Column(
        Integer,
        default=90,
        nullable=False,
        comment="Har bir savol uchun vaqt"
    )
    qolgan_vaqt = Column(
        Integer,
        nullable=True,
        comment="Qolgan vaqt (soniyalarda)"
    )
    
    # Vaqtlar
    boshlangan_vaqt = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="Boshlangan vaqt"
    )
    tugallangan_vaqt = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="Tugallangan vaqt"
    )
    
    # Savollar (holat_id lar ro'yxati)
    savollar = Column(
        ARRAY(UUID(as_uuid=True)),
        nullable=False,
        default=[],
        comment="Savollar ro'yxati (holat_id)"
    )
    joriy_savol_indeksi = Column(
        Integer,
        default=0,
        nullable=False,
        comment="Joriy savol indeksi"
    )
    
    # Sozlamalar
    aralashtirish = Column(Boolean, default=True)
    orqaga_qaytish = Column(Boolean, default=True)
    natijani_korsatish = Column(Boolean, default=False)
    
    # Statistika
    jami_savollar = Column(
        Integer,
        default=0,
        nullable=False,
        comment="Jami savollar soni"
    )
    javob_berilgan = Column(
        Integer,
        default=0,
        nullable=False,
        comment="Javob berilgan savollar"
    )
    togri_javoblar = Column(
        Integer,
        default=0,
        nullable=False,
        comment="To'g'ri javoblar"
    )
    notogri_javoblar = Column(
        Integer,
        default=0,
        nullable=False,
        comment="Noto'g'ri javoblar"
    )
    otkazilgan_savollar = Column(
        Integer,
        default=0,
        nullable=False,
        comment="O'tkazib yuborilgan savollar"
    )
    
    # Natija
    ball_foizi = Column(
        Integer,
        nullable=True,
        comment="Ball foizi (0-100)"
    )
    otish_balli = Column(
        Integer,
        default=60,
        nullable=False,
        comment="O'tish balli"
    )
    otgan = Column(
        Boolean,
        nullable=True,
        comment="O'tgan/o'tmagan"
    )
    
    # Munosabatlar
    foydalanuvchi = relationship("Foydalanuvchi", back_populates="imtihonlar")
    shablon = relationship("ImtihonShabloni", back_populates="imtihonlar")
    javoblar = relationship(
        "ImtihonJavobi",
        back_populates="imtihon",
        cascade="all, delete-orphan",
        order_by="ImtihonJavobi.savol_indeksi"
    )
    
    __table_args__ = (
        Index("idx_imtihon_foydalanuvchi_holat", "foydalanuvchi_id", "holat"),
        Index("idx_imtihon_vaqt", "boshlangan_vaqt"),
    )
    
    @property
    def sarflangan_vaqt(self) -> int:
        """Sarflangan vaqtni hisoblash."""
        if not self.boshlangan_vaqt:
            return 0
        tugash = self.tugallangan_vaqt or datetime.utcnow()
        return int((tugash - self.boshlangan_vaqt).total_seconds())
    
    @property
    def aniqlik_foizi(self) -> float:
        """Aniqlik foizini hisoblash."""
        if self.javob_berilgan == 0:
            return 0.0
        return (self.togri_javoblar / self.javob_berilgan) * 100


class ImtihonJavobi(AsosiyModel):
    """Imtihon davomida berilgan javoblar."""
    __tablename__ = "imtihon_javoblari"
    
    # Bog'lanishlar
    imtihon_id = Column(
        UUID(as_uuid=True),
        ForeignKey("imtihonlar.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Imtihon ID"
    )
    holat_id = Column(
        UUID(as_uuid=True),
        ForeignKey("holatlar.id", ondelete="CASCADE"),
        nullable=False,
        comment="Holat (savol) ID"
    )
    
    # Javob
    savol_indeksi = Column(
        Integer,
        nullable=False,
        comment="Savol indeksi (tartib raqami)"
    )
    tanlangan_javob = Column(
        String(1),
        nullable=True,
        comment="Tanlangan javob (A/B/C/D yoki null)"
    )
    togri_javob = Column(
        String(1),
        nullable=False,
        comment="To'g'ri javob"
    )
    togri = Column(
        Boolean,
        nullable=True,
        comment="Javob to'g'riligi"
    )
    
    # Vaqt
    savol_boshlangan = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="Savol ko'rsatilgan vaqt"
    )
    javob_berilgan_vaqt = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="Javob berilgan vaqt"
    )
    sarflangan_vaqt = Column(
        Integer,
        nullable=True,
        comment="Sarflangan vaqt (soniyalarda)"
    )
    
    # Holat
    otkazilgan = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="O'tkazib yuborilgan"
    )
    belgilangan = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="Keyinroq ko'rish uchun belgilangan"
    )
    
    # Munosabatlar
    imtihon = relationship("Imtihon", back_populates="javoblar")
    holat = relationship("Holat")
    
    __table_args__ = (
        Index("idx_javob_imtihon_indeks", "imtihon_id", "savol_indeksi", unique=True),
    )
