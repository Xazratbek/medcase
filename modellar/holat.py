# MedCase Pro Platform - Holat (Case) Modellari
# Klinik holatlar, variantlar va media

from sqlalchemy import (
    Column, String, Integer, ForeignKey, Text,
    Boolean, Enum as SQLEnum, Index, Table
)
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship
import enum

from modellar.asosiy import AsosiyModel


class HolatTuri(str, enum.Enum):
    """Holat turlari."""
    MCQ = "mcq"  # Ko'p tanlovli savol
    KLINIK_VINYET = "klinik_vinyet"  # Klinik stsenariy
    RASM_ASOSLI = "rasm_asosli"  # Rasm asosidagi savol
    VIDEO_ASOSLI = "video_asosli"  # Video asosidagi savol


class QiyinlikDarajasi(str, enum.Enum):
    """Qiyinlik darajalari."""
    OSON = "oson"
    ORTACHA = "ortacha"
    QIYIN = "qiyin"


class MediaTuri(str, enum.Enum):
    """Media turlari."""
    RASM = "rasm"
    VIDEO = "video"
    RENTGEN = "rentgen"
    KT = "kt"  # Kompyuter tomografiya
    MRT = "mrt"  # Magnit rezonans tomografiya
    ULTRATOVUSH = "ultratovush"
    EKG = "ekg"
    LABORATORIYA = "laboratoriya"
    PATOLOGIYA = "patologiya"


# Holat va teglar bog'lanishi (many-to-many)
holat_teglar = Table(
    "holat_teglar",
    AsosiyModel.metadata,
    Column(
        "holat_id",
        UUID(as_uuid=True),
        ForeignKey("holatlar.id", ondelete="CASCADE"),
        primary_key=True
    ),
    Column(
        "teg_id",
        UUID(as_uuid=True),
        ForeignKey("teglar.id", ondelete="CASCADE"),
        primary_key=True
    )
)


class Holat(AsosiyModel):
    """
    Klinik holat modeli.
    Asosiy o'quv kontenti - savollar va javoblar.
    """
    __tablename__ = "holatlar"
    
    # Bog'lanish
    bolim_id = Column(
        UUID(as_uuid=True),
        ForeignKey("bolimlar.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Bo'lim ID"
    )
    
    # Asosiy maydonlar
    sarlavha = Column(
        String(500),
        nullable=False,
        comment="Holat sarlavhasi"
    )
    klinik_stsenariy = Column(
        Text,
        nullable=False,
        comment="Klinik stsenariy - bemor tarixi va simptomlar"
    )
    savol = Column(
        Text,
        nullable=False,
        comment="Asosiy savol"
    )
    
    # Javob
    togri_javob = Column(
        String(1),
        nullable=False,
        comment="To'g'ri javob (A, B, C, D)"
    )
    umumiy_tushuntirish = Column(
        Text,
        nullable=True,
        comment="Umumiy tushuntirish"
    )
    
    # Holat turi va qiyinlik
    turi = Column(
        SQLEnum(HolatTuri),
        default=HolatTuri.MCQ,
        nullable=False,
        index=True,
        comment="Holat turi"
    )
    qiyinlik = Column(
        SQLEnum(QiyinlikDarajasi),
        default=QiyinlikDarajasi.ORTACHA,
        nullable=False,
        index=True,
        comment="Qiyinlik darajasi"
    )
    
    # Qo'shimcha kontekst
    klinik_kontekst = Column(
        Text,
        nullable=True,
        comment="Qo'shimcha klinik ma'lumot"
    )
    
    # Ball va vaqt
    ball = Column(
        Integer,
        default=10,
        nullable=False,
        comment="Berilgan ball"
    )
    tavsiya_vaqt = Column(
        Integer,
        default=120,
        nullable=False,
        comment="Tavsiya etilgan vaqt (soniyalarda)"
    )
    
    # Statistika
    urinishlar_soni = Column(
        Integer,
        default=0,
        nullable=False,
        comment="Jami urinishlar soni"
    )
    togri_javoblar = Column(
        Integer,
        default=0,
        nullable=False,
        comment="To'g'ri javoblar soni"
    )
    
    # Holat ma'lumotlari
    chop_etilgan = Column(
        Boolean,
        default=False,
        nullable=False,
        index=True,
        comment="Chop etilgan holati"
    )
    tekshirilgan = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="Tekshirilgan holati"
    )
    
    # Munosabatlar
    bolim = relationship("Bolim", back_populates="holatlar")
    variantlar = relationship(
        "HolatVarianti",
        back_populates="holat",
        cascade="all, delete-orphan",
        order_by="HolatVarianti.belgi"
    )
    media = relationship(
        "HolatMedia",
        back_populates="holat",
        cascade="all, delete-orphan"
    )
    teglar = relationship(
        "HolatTegi",
        secondary=holat_teglar,
        back_populates="holatlar"
    )
    urinishlar = relationship(
        "HolatUrinishi",
        back_populates="holat",
        cascade="all, delete-orphan"
    )
    izohlar = relationship(
        "HolatIzohi",
        back_populates="holat",
        cascade="all, delete-orphan"
    )
    takrorlash_kartalari = relationship(
        "TakrorlashKartasi",
        back_populates="holat",
        cascade="all, delete-orphan"
    )
    
    # Indekslar
    __table_args__ = (
        Index("idx_holat_bolim_chop", "bolim_id", "chop_etilgan"),
        Index("idx_holat_qiyinlik_chop", "qiyinlik", "chop_etilgan"),
        Index("idx_holat_turi_chop", "turi", "chop_etilgan"),
    )
    
    @property
    def muvaffaqiyat_foizi(self) -> float:
        """Muvaffaqiyat foizini hisoblaydi."""
        if self.urinishlar_soni == 0:
            return 0.0
        return (self.togri_javoblar / self.urinishlar_soni) * 100


class HolatVarianti(AsosiyModel):
    """Holat variantlari modeli (A, B, C, D)."""
    __tablename__ = "holat_variantlari"
    
    holat_id = Column(
        UUID(as_uuid=True),
        ForeignKey("holatlar.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Holat ID"
    )
    
    belgi = Column(
        String(1),
        nullable=False,
        comment="Variant belgisi (A, B, C, D)"
    )
    matn = Column(
        Text,
        nullable=False,
        comment="Variant matni"
    )
    tushuntirish = Column(
        Text,
        nullable=True,
        comment="Nima uchun to'g'ri/noto'g'ri"
    )
    togri = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="To'g'ri variant"
    )
    
    holat = relationship("Holat", back_populates="variantlar")
    
    __table_args__ = (
        Index("idx_variant_holat_belgi", "holat_id", "belgi", unique=True),
    )


class HolatMedia(AsosiyModel):
    """Holat media fayllari modeli."""
    __tablename__ = "holat_media"
    
    holat_id = Column(
        UUID(as_uuid=True),
        ForeignKey("holatlar.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Holat ID"
    )
    
    turi = Column(
        SQLEnum(MediaTuri),
        nullable=False,
        comment="Media turi"
    )
    url = Column(
        String(500),
        nullable=False,
        comment="Media URL (Cloudinary)"
    )
    nom = Column(
        String(255),
        nullable=True,
        comment="Media nomi"
    )
    tavsif = Column(
        Text,
        nullable=True,
        comment="Media tavsifi"
    )
    tartib = Column(
        Integer,
        default=0,
        nullable=False,
        comment="Ko'rsatish tartibi"
    )
    
    # Cloudinary ma'lumotlari
    cloudinary_id = Column(
        String(255),
        nullable=True,
        comment="Cloudinary public ID"
    )
    fayl_hajmi = Column(
        Integer,
        nullable=True,
        comment="Fayl hajmi (baytlarda)"
    )
    kenglik = Column(Integer, nullable=True, comment="Rasm kengligi")
    balandlik = Column(Integer, nullable=True, comment="Rasm balandligi")
    davomiylik = Column(Integer, nullable=True, comment="Video davomiyligi")
    
    holat = relationship("Holat", back_populates="media")


class HolatTegi(AsosiyModel):
    """Holat teglari modeli."""
    __tablename__ = "teglar"
    
    nom = Column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
        comment="Teg nomi"
    )
    slug = Column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
        comment="Teg slug"
    )
    rang = Column(
        String(7),
        default="#6B7280",
        nullable=False,
        comment="Teg rangi"
    )
    
    holatlar = relationship(
        "Holat",
        secondary=holat_teglar,
        back_populates="teglar"
    )
