# MedCase Pro Platform - Kategoriya Modellari
# Uch bosqichli taksonomiya: Asosiy kategoriya -> Kichik kategoriya -> Bo'lim

from sqlalchemy import (
    Column, String, Integer, ForeignKey, Text, Index
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from modellar.asosiy import AsosiyModel


class AsosiyKategoriya(AsosiyModel):
    """
    Asosiy kategoriya modeli (Level 1).
    Masalan: Fundamental fanlar, Klinik fanlar, Pre-klinik fanlar
    """
    __tablename__ = "asosiy_kategoriyalar"
    
    # Asosiy maydonlar
    nomi = Column(
        String(255),
        unique=True,
        nullable=False,
        comment="Kategoriya nomi"
    )
    slug = Column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
        comment="URL uchun slug"
    )
    tavsif = Column(
        Text,
        nullable=True,
        comment="Kategoriya tavsifi"
    )
    
    # Vizual
    rasm_url = Column(
        String(500),
        nullable=True,
        comment="Kategoriya rasmi URL"
    )
    rang = Column(
        String(7),
        default="#3B82F6",
        nullable=False,
        comment="Kategoriya rangi (HEX)"
    )
    ikonka = Column(
        String(50),
        nullable=True,
        comment="Ikonka nomi"
    )
    
    # Tartib
    tartib = Column(
        Integer,
        default=0,
        nullable=False,
        index=True,
        comment="Ko'rsatish tartibi"
    )
    
    # Statistika (denormalizatsiya - tezlik uchun)
    holatlar_soni = Column(
        Integer,
        default=0,
        nullable=False,
        comment="Jami holatlar soni"
    )
    
    # Munosabatlar
    kichik_kategoriyalar = relationship(
        "KichikKategoriya",
        back_populates="asosiy_kategoriya",
        cascade="all, delete-orphan",
        order_by="KichikKategoriya.tartib"
    )


class KichikKategoriya(AsosiyModel):
    """
    Kichik kategoriya modeli (Level 2).
    Masalan: Anatomiya, Fiziologiya, Biokimyo, Farmakologiya
    """
    __tablename__ = "kichik_kategoriyalar"
    
    # Bog'lanish
    asosiy_kategoriya_id = Column(
        UUID(as_uuid=True),
        ForeignKey("asosiy_kategoriyalar.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Asosiy kategoriya ID"
    )
    
    # Asosiy maydonlar
    nomi = Column(
        String(255),
        nullable=False,
        comment="Kichik kategoriya nomi"
    )
    slug = Column(
        String(255),
        nullable=False,
        index=True,
        comment="URL uchun slug"
    )
    tavsif = Column(
        Text,
        nullable=True,
        comment="Tavsif"
    )
    
    # Vizual
    rasm_url = Column(
        String(500),
        nullable=True,
        comment="Rasm URL"
    )
    rang = Column(
        String(7),
        default="#10B981",
        nullable=False,
        comment="Rang (HEX)"
    )
    ikonka = Column(
        String(50),
        nullable=True,
        comment="Ikonka nomi"
    )
    
    # Tartib
    tartib = Column(
        Integer,
        default=0,
        nullable=False,
        index=True,
        comment="Ko'rsatish tartibi"
    )
    
    # Statistika
    holatlar_soni = Column(
        Integer,
        default=0,
        nullable=False,
        comment="Jami holatlar soni"
    )
    
    # Munosabatlar
    asosiy_kategoriya = relationship(
        "AsosiyKategoriya",
        back_populates="kichik_kategoriyalar"
    )
    bolimlar = relationship(
        "Bolim",
        back_populates="kichik_kategoriya",
        cascade="all, delete-orphan",
        order_by="Bolim.tartib"
    )
    
    @property
    def bolimlar_soni(self) -> int:
        """Bo'limlar sonini qaytaradi."""
        return len(self.bolimlar) if self.bolimlar else 0
    
    # Indekslar
    __table_args__ = (
        Index(
            "idx_kichik_kategoriya_slug_unique",
            "asosiy_kategoriya_id",
            "slug",
            unique=True
        ),
    )


class Bolim(AsosiyModel):
    """
    Bo'lim modeli (Level 3).
    Masalan: Yurak-qon tomir tizimi, Nafas olish tizimi, Siydik-jinsiy tizim
    """
    __tablename__ = "bolimlar"
    
    # Bog'lanish
    kichik_kategoriya_id = Column(
        UUID(as_uuid=True),
        ForeignKey("kichik_kategoriyalar.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Kichik kategoriya ID"
    )
    
    # Asosiy maydonlar
    nomi = Column(
        String(255),
        nullable=False,
        comment="Bo'lim nomi"
    )
    slug = Column(
        String(255),
        nullable=False,
        index=True,
        comment="URL uchun slug"
    )
    tavsif = Column(
        Text,
        nullable=True,
        comment="Tavsif"
    )
    
    # Vizual
    rasm_url = Column(
        String(500),
        nullable=True,
        comment="Rasm URL"
    )
    rang = Column(
        String(7),
        default="#8B5CF6",
        nullable=False,
        comment="Rang (HEX)"
    )
    ikonka = Column(
        String(50),
        nullable=True,
        comment="Ikonka nomi"
    )
    
    # Tartib
    tartib = Column(
        Integer,
        default=0,
        nullable=False,
        index=True,
        comment="Ko'rsatish tartibi"
    )
    
    # Statistika
    holatlar_soni = Column(
        Integer,
        default=0,
        nullable=False,
        comment="Jami holatlar soni"
    )
    oson_holatlar = Column(
        Integer,
        default=0,
        nullable=False,
        comment="Oson holatlar soni"
    )
    ortacha_holatlar = Column(
        Integer,
        default=0,
        nullable=False,
        comment="O'rtacha holatlar soni"
    )
    qiyin_holatlar = Column(
        Integer,
        default=0,
        nullable=False,
        comment="Qiyin holatlar soni"
    )
    
    # Munosabatlar
    kichik_kategoriya = relationship(
        "KichikKategoriya",
        back_populates="bolimlar"
    )
    holatlar = relationship(
        "Holat",
        back_populates="bolim",
        cascade="all, delete-orphan"
    )
    
    # Indekslar
    __table_args__ = (
        Index(
            "idx_bolim_slug_unique",
            "kichik_kategoriya_id",
            "slug",
            unique=True
        ),
    )
