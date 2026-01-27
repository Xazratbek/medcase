# MedCase Pro Platform - Obuna va To'lov Modellari
# Obuna darajalari, foydalanuvchi obunalari va to'lovlar

from sqlalchemy import (
    Column, String, Integer, ForeignKey, Text,
    Boolean, Float, DateTime, Enum as SQLEnum, Index
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import enum

from modellar.asosiy import AsosiyModel


class ObunaDarajasi(str, enum.Enum):
    """Obuna darajalari."""
    BEPUL = "bepul"
    TALABA = "talaba"
    PROFESSIONAL = "professional"
    MUASSASA = "muassasa"


class TolovHolati(str, enum.Enum):
    """To'lov holatlari."""
    KUTILMOQDA = "kutilmoqda"
    MUVAFFAQIYATLI = "muvaffaqiyatli"
    BEKOR_QILINGAN = "bekor_qilingan"
    QAYTARILGAN = "qaytarilgan"
    XATO = "xato"


class TolovUsuli(str, enum.Enum):
    """To'lov usullari."""
    KARTA = "karta"
    PAYME = "payme"
    CLICK = "click"
    UZCARD = "uzcard"
    HUMO = "humo"
    PAYPAL = "paypal"


class ObunaTarifi(AsosiyModel):
    """Obuna tariflari modeli."""
    __tablename__ = "obuna_tariflari"
    
    nom = Column(
        String(100),
        unique=True,
        nullable=False,
        comment="Tarif nomi"
    )
    kod = Column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
        comment="Tarif kodi"
    )
    daraja = Column(
        SQLEnum(ObunaDarajasi),
        nullable=False,
        index=True,
        comment="Obuna darajasi"
    )
    tavsif = Column(
        Text,
        nullable=True,
        comment="Tarif tavsifi"
    )
    
    # Narx
    oylik_narx = Column(
        Integer,
        default=0,
        nullable=False,
        comment="Oylik narx (so'mda)"
    )
    yillik_narx = Column(
        Integer,
        default=0,
        nullable=False,
        comment="Yillik narx (so'mda)"
    )
    valyuta = Column(
        String(3),
        default="UZS",
        nullable=False,
        comment="Valyuta"
    )
    
    # Imkoniyatlar (JSONB)
    imkoniyatlar = Column(
        JSONB,
        default={},
        nullable=False,
        comment="Tarif imkoniyatlari"
    )
    # Masalan: {"kunlik_limit": 50, "video_ruxsat": true, "yuklab_olish": true}
    
    # Cheklovlar
    kunlik_holat_limiti = Column(
        Integer,
        nullable=True,
        comment="Kunlik holat limiti (null = cheksiz)"
    )
    
    # Vizual
    rang = Column(
        String(7),
        default="#3B82F6",
        nullable=False,
        comment="Tarif rangi"
    )
    mashhur = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="Mashhur tarif belgisi"
    )
    
    obunalar = relationship(
        "Obuna",
        back_populates="tarif",
        cascade="all, delete-orphan"
    )


class Obuna(AsosiyModel):
    """Foydalanuvchi obunasi modeli."""
    __tablename__ = "obunalar"
    
    foydalanuvchi_id = Column(
        UUID(as_uuid=True),
        ForeignKey("foydalanuvchilar.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        comment="Foydalanuvchi ID"
    )
    tarif_id = Column(
        UUID(as_uuid=True),
        ForeignKey("obuna_tariflari.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
        comment="Tarif ID"
    )
    
    # Vaqtlar
    boshlangan_vaqt = Column(
        DateTime(timezone=True),
        nullable=False,
        comment="Obuna boshlanish vaqti"
    )
    tugash_vaqti = Column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
        comment="Obuna tugash vaqti"
    )
    
    # Holat
    faol = Column(
        Boolean,
        default=True,
        nullable=False,
        index=True,
        comment="Obuna faol"
    )
    avtomatik_yangilash = Column(
        Boolean,
        default=True,
        nullable=False,
        comment="Avtomatik yangilash"
    )
    
    # Sinov
    sinov_davrida = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="Sinov davrida"
    )
    sinov_tugash_vaqti = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="Sinov tugash vaqti"
    )
    
    # Bekor qilish
    bekor_qilingan = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="Bekor qilingan"
    )
    bekor_qilish_vaqti = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="Bekor qilish vaqti"
    )
    bekor_qilish_sababi = Column(
        Text,
        nullable=True,
        comment="Bekor qilish sababi"
    )
    
    foydalanuvchi = relationship("Foydalanuvchi", back_populates="obuna")
    tarif = relationship("ObunaTarifi", back_populates="obunalar")
    tolovlar = relationship(
        "Tolov",
        back_populates="obuna",
        cascade="all, delete-orphan"
    )


class Tolov(AsosiyModel):
    """To'lov modeli."""
    __tablename__ = "tolovlar"
    
    obuna_id = Column(
        UUID(as_uuid=True),
        ForeignKey("obunalar.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Obuna ID"
    )
    
    # To'lov ma'lumotlari
    miqdor = Column(
        Integer,
        nullable=False,
        comment="To'lov miqdori"
    )
    valyuta = Column(
        String(3),
        default="UZS",
        nullable=False,
        comment="Valyuta"
    )
    
    # To'lov usuli
    usul = Column(
        SQLEnum(TolovUsuli),
        nullable=False,
        comment="To'lov usuli"
    )
    
    # Holat
    holat = Column(
        SQLEnum(TolovHolati),
        default=TolovHolati.KUTILMOQDA,
        nullable=False,
        index=True,
        comment="To'lov holati"
    )
    
    # Tashqi tizim ma'lumotlari
    tashqi_id = Column(
        String(255),
        nullable=True,
        index=True,
        comment="Tashqi tizim tranzaksiya ID"
    )
    tashqi_javob = Column(
        JSONB,
        nullable=True,
        comment="Tashqi tizim javobi"
    )
    
    # Vaqtlar
    tolov_vaqti = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="To'lov amalga oshirilgan vaqt"
    )
    
    # Hisob-faktura
    hisob_faktura_raqami = Column(
        String(50),
        unique=True,
        nullable=True,
        comment="Hisob-faktura raqami"
    )
    
    obuna = relationship("Obuna", back_populates="tolovlar")
    
    __table_args__ = (
        Index("idx_tolov_holat_vaqt", "holat", "yaratilgan_vaqt"),
    )
