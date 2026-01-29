# MedCase Pro Platform - Bildirishnoma Modellari
# Foydalanuvchi bildirshnomalari va sozlamalari

from sqlalchemy import (
    Column, String, Integer, ForeignKey, Text,
    Boolean, DateTime, Enum as SQLEnum, Index
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import enum

from modellar.asosiy import AsosiyModel


class BildirishnomaTuri(str, enum.Enum):
    """Bildirishnoma turlari."""
    TIZIM = "tizim"  # Tizim bildirshnomalari
    YUTUQ = "yutuq"  # Yangi yutuq
    NISHON = "nishon"  # Yangi nishon
    STREAK = "streak"  # Streak eslatmasi
    REYTING = "reyting"  # Reyting o'zgarishi
    YANGI_KONTENT = "yangi_kontent"  # Yangi holatlar
    ESLATMA = "eslatma"  # O'qish eslatmasi
    OBUNA = "obuna"  # Obuna bilan bog'liq
    MUASSASA = "muassasa"  # Muassasa e'lonlari


class Bildirishnoma(AsosiyModel):
    """Bildirishnoma modeli."""
    __tablename__ = "bildirishnomalar"
    
    foydalanuvchi_id = Column(
        UUID(as_uuid=True),
        ForeignKey("foydalanuvchilar.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Foydalanuvchi ID"
    )
    
    # Bildirishnoma ma'lumotlari
    turi = Column(
        SQLEnum(BildirishnomaTuri),
        nullable=False,
        index=True,
        comment="Bildirishnoma turi"
    )
    sarlavha = Column(
        String(255),
        nullable=False,
        comment="Sarlavha"
    )
    matn = Column(
        Text,
        nullable=False,
        comment="Bildirishnoma matni"
    )
    
    # Qo'shimcha ma'lumotlar
    qoshimcha_malumot = Column(
        JSONB,
        default={},
        nullable=False,
        comment="Qo'shimcha ma'lumotlar"
    )
    # Masalan: {"nishon_id": "...", "holat_id": "..."}
    
    # Havola
    havola = Column(
        String(500),
        nullable=True,
        comment="Havola URL"
    )
    
    # Holat
    oqilgan = Column(
        Boolean,
        default=False,
        nullable=False,
        index=True,
        comment="O'qilgan holati"
    )
    oqilgan_vaqt = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="O'qilgan vaqt"
    )
    
    foydalanuvchi = relationship(
        "Foydalanuvchi",
        back_populates="bildirishnomalar"
    )
    
    __table_args__ = (
        Index("idx_bildirishnoma_foyd_oqilgan", "foydalanuvchi_id", "oqilgan"),
        Index("idx_bildirishnoma_vaqt", "yaratilgan_vaqt"),
    )


class BildirishnomaSozlamalari(AsosiyModel):
    """Bildirishnoma sozlamalari modeli."""
    __tablename__ = "bildirishnoma_sozlamalari"
    
    foydalanuvchi_id = Column(
        UUID(as_uuid=True),
        ForeignKey("foydalanuvchilar.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        comment="Foydalanuvchi ID"
    )
    
    # Email bildirshnomalari
    email_yutuqlar = Column(Boolean, default=True, nullable=False)
    email_streak = Column(Boolean, default=True, nullable=False)
    email_yangi_kontent = Column(Boolean, default=False, nullable=False)
    email_haftalik_hisobot = Column(Boolean, default=True, nullable=False)
    
    # Push bildirshnomalari
    push_yutuqlar = Column(Boolean, default=True, nullable=False)
    push_streak = Column(Boolean, default=True, nullable=False)
    push_eslatma = Column(Boolean, default=True, nullable=False)
    push_reyting = Column(Boolean, default=True, nullable=False)
    push_yangi_kontent = Column(Boolean, default=True, nullable=False)
    
    # Ilova ichidagi bildirishnomalar
    ilova_yutuqlar = Column(Boolean, default=True, nullable=False)
    ilova_streak = Column(Boolean, default=True, nullable=False)
    ilova_yangi_kontent = Column(Boolean, default=True, nullable=False)
    ilova_tizim = Column(Boolean, default=True, nullable=False)
    
    # Eslatma vaqtlari (JSONB)
    eslatma_vaqtlari = Column(
        JSONB,
        default={"soat": 9, "daqiqa": 0, "kunlar": [1, 2, 3, 4, 5]},
        nullable=False,
        comment="Eslatma vaqtlari"
    )
    
    # Sokin rejim
    sokin_rejim = Column(Boolean, default=False, nullable=False)
    sokin_boshlanish = Column(String(5), default="22:00", nullable=False)
    sokin_tugash = Column(String(5), default="08:00", nullable=False)


class PushObuna(AsosiyModel):
    """Web Push obunasi."""
    __tablename__ = "push_obunalar"

    foydalanuvchi_id = Column(
        UUID(as_uuid=True),
        ForeignKey("foydalanuvchilar.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Foydalanuvchi ID"
    )
    endpoint = Column(
        String(1024),
        nullable=False,
        unique=True,
        comment="Push endpoint"
    )
    p256dh = Column(String(255), nullable=False)
    auth = Column(String(255), nullable=False)
    content_encoding = Column(String(20), default="aesgcm", nullable=False)
    user_agent = Column(String(255), nullable=True)

    foydalanuvchi = relationship("Foydalanuvchi", back_populates="push_obunalar")

    __table_args__ = (
        Index("idx_push_obuna_foyd", "foydalanuvchi_id"),
    )
