# MedCase Pro Platform - Gamifikatsiya Modellari
# Nishonlar, ballar, reytinglar

from sqlalchemy import (
    Column, String, Integer, ForeignKey, Text,
    Boolean, Float, DateTime, Enum as SQLEnum, Index
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import enum

from modellar.asosiy import AsosiyModel


class NishonTuri(str, enum.Enum):
    """Nishon turlari."""
    BOSQICH = "bosqich"  # Milestone badges
    MAHORAT = "mahorat"  # Mastery badges
    ANIQLIK = "aniqlik"  # Accuracy badges
    TEZLIK = "tezlik"  # Speed badges
    STREAK = "streak"  # Streak badges
    TADQIQOTCHI = "tadqiqotchi"  # Explorer badges
    MUKAMMAL = "mukammal"  # Perfectionist badges
    SADOQAT = "sadoqat"  # Dedication badges
    IJTIMOIY = "ijtimoiy"  # Social badges
    MUTAXASSISLIK = "mutaxassislik"  # Specialty badges


class NishonNodirligi(str, enum.Enum):
    """Nishon nodirligi."""
    ODDIY = "oddiy"  # Common
    NODIR = "nodir"  # Rare
    EPIK = "epik"  # Epic
    AFSONAVIY = "afsonaviy"  # Legendary


class Nishon(AsosiyModel):
    """
    Nishon (Badge) modeli.
    Foydalanuvchilar qo'lga kiritishi mumkin bo'lgan yutuqlar.
    """
    __tablename__ = "nishonlar"
    
    # Asosiy ma'lumotlar
    nom = Column(
        String(100),
        unique=True,
        nullable=False,
        comment="Nishon nomi"
    )
    kod = Column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
        comment="Nishon kodi"
    )
    tavsif = Column(
        Text,
        nullable=False,
        comment="Nishon tavsifi"
    )
    
    # Tur va nodirlik
    turi = Column(
        SQLEnum(NishonTuri),
        nullable=False,
        index=True,
        comment="Nishon turi"
    )
    nodirlik = Column(
        SQLEnum(NishonNodirligi),
        default=NishonNodirligi.ODDIY,
        nullable=False,
        index=True,
        comment="Nodirlik darajasi"
    )
    
    # Vizual
    ikonka_url = Column(
        String(500),
        nullable=True,
        comment="Ikonka URL"
    )
    rang = Column(
        String(7),
        default="#FFD700",
        nullable=False,
        comment="Nishon rangi"
    )
    
    # Qiymat
    ball_qiymati = Column(
        Integer,
        default=100,
        nullable=False,
        comment="Nishon ball qiymati"
    )
    
    # Ochish shartlari (JSONB)
    ochish_shartlari = Column(
        JSONB,
        nullable=False,
        comment="Ochish shartlari"
    )
    # Masalan: {"turi": "holatlar_soni", "qiymat": 100}
    # {"turi": "streak", "qiymat": 7}
    # {"turi": "aniqlik", "qiymat": 90, "kategoriya_id": "..."}
    
    # Statistika
    ega_bolganlar_soni = Column(
        Integer,
        default=0,
        nullable=False,
        comment="Ega bo'lganlar soni"
    )
    
    # Munosabatlar
    foydalanuvchi_nishonlari = relationship(
        "FoydalanuvchiNishoni",
        back_populates="nishon",
        cascade="all, delete-orphan"
    )


class FoydalanuvchiNishoni(AsosiyModel):
    """
    Foydalanuvchi nishonlari modeli.
    Foydalanuvchi qo'lga kiritgan nishonlar.
    """
    __tablename__ = "foydalanuvchi_nishonlari"
    
    foydalanuvchi_id = Column(
        UUID(as_uuid=True),
        ForeignKey("foydalanuvchilar.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Foydalanuvchi ID"
    )
    nishon_id = Column(
        UUID(as_uuid=True),
        ForeignKey("nishonlar.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Nishon ID"
    )
    
    # Qo'lga kiritish
    qolga_kiritilgan_vaqt = Column(
        DateTime(timezone=True),
        nullable=False,
        comment="Qo'lga kiritilgan vaqt"
    )
    
    # Ko'rsatish
    profilda_korsatish = Column(
        Boolean,
        default=True,
        nullable=False,
        comment="Profilda ko'rsatish"
    )
    
    # Munosabatlar
    foydalanuvchi = relationship("Foydalanuvchi", back_populates="nishonlar")
    nishon = relationship("Nishon", back_populates="foydalanuvchi_nishonlari")
    
    # Indekslar
    __table_args__ = (
        Index(
            "idx_foyd_nishon_unique",
            "foydalanuvchi_id",
            "nishon_id",
            unique=True
        ),
    )


class Ball(AsosiyModel):
    """
    Ball tarixi modeli.
    Foydalanuvchi olgan barcha ballar tarixi.
    """
    __tablename__ = "ballar"
    
    foydalanuvchi_id = Column(
        UUID(as_uuid=True),
        ForeignKey("foydalanuvchilar.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Foydalanuvchi ID"
    )
    
    # Ball ma'lumotlari
    miqdor = Column(
        Integer,
        nullable=False,
        comment="Ball miqdori"
    )
    sabab = Column(
        String(100),
        nullable=False,
        comment="Ball sababi"
    )
    tavsif = Column(
        String(255),
        nullable=True,
        comment="Qo'shimcha tavsif"
    )
    
    # Bog'lanish (agar mavjud bo'lsa)
    holat_id = Column(
        UUID(as_uuid=True),
        ForeignKey("holatlar.id", ondelete="SET NULL"),
        nullable=True,
        comment="Holat ID"
    )
    nishon_id = Column(
        UUID(as_uuid=True),
        ForeignKey("nishonlar.id", ondelete="SET NULL"),
        nullable=True,
        comment="Nishon ID"
    )
    
    # Munosabatlar
    foydalanuvchi = relationship("Foydalanuvchi", back_populates="balllar")


class Reyting(AsosiyModel):
    """
    Reyting modeli.
    Foydalanuvchilar reytingi turli kategoriyalar bo'yicha.
    """
    __tablename__ = "reytinglar"
    
    foydalanuvchi_id = Column(
        UUID(as_uuid=True),
        ForeignKey("foydalanuvchilar.id", ondelete="CASCADE"),
        nullable=False,
        comment="Foydalanuvchi ID"
    )
    
    # Reyting turi
    turi = Column(
        String(50),
        nullable=False,
        index=True,
        comment="Reyting turi (global/haftalik/oylik/kategoriya)"
    )
    
    # Kategoriya (agar kategoriya bo'yicha bo'lsa)
    kategoriya_id = Column(
        UUID(as_uuid=True),
        ForeignKey("asosiy_kategoriyalar.id", ondelete="CASCADE"),
        nullable=True,
        comment="Kategoriya ID"
    )
    
    # Reyting ma'lumotlari
    orni = Column(
        Integer,
        nullable=False,
        index=True,
        comment="Reyting o'rni"
    )
    ball = Column(
        Integer,
        nullable=False,
        comment="Jami ball"
    )
    holatlar_soni = Column(
        Integer,
        nullable=False,
        comment="Yechilgan holatlar soni"
    )
    aniqlik = Column(
        Float,
        nullable=False,
        comment="Aniqlik foizi"
    )
    
    # Davr
    davr_boshlanishi = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="Davr boshlanishi"
    )
    davr_tugashi = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="Davr tugashi"
    )
    
    # Indekslar
    __table_args__ = (
        Index("idx_reyting_turi_orni", "turi", "orni"),
        Index("idx_reyting_foyd_turi", "foydalanuvchi_id", "turi"),
    )


class DarajaKonfiguratsiyasi(AsosiyModel):
    """
    Daraja konfiguratsiyasi modeli.
    Har bir daraja uchun kerakli ball va imkoniyatlar.
    """
    __tablename__ = "daraja_konfiguratsiyasi"
    
    daraja = Column(
        Integer,
        unique=True,
        nullable=False,
        index=True,
        comment="Daraja raqami"
    )
    nom = Column(
        String(100),
        nullable=False,
        comment="Daraja nomi"
    )
    kerakli_ball = Column(
        Integer,
        nullable=False,
        comment="Kerakli ball"
    )
    
    # Vizual
    ikonka_url = Column(
        String(500),
        nullable=True,
        comment="Daraja ikonkasi"
    )
    rang = Column(
        String(7),
        default="#3B82F6",
        nullable=False,
        comment="Daraja rangi"
    )
    
    # Imkoniyatlar (JSONB)
    imkoniyatlar = Column(
        JSONB,
        default={},
        nullable=False,
        comment="Daraja imkoniyatlari"
    )
