# MedCase Pro Platform - Izoh (Comment) Modellari
# Holatlarga izoh qoldirish va muhokama

from sqlalchemy import (
    Column, String, Integer, ForeignKey, Text,
    Boolean, DateTime, Index, func
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from modellar.asosiy import AsosiyModel


class HolatIzohi(AsosiyModel):
    """
    Holat izohi modeli.
    Foydalanuvchilar holatlar haqida izoh qoldirishlari.
    """
    __tablename__ = "holat_izohlari"
    
    # Bog'lanishlar
    holat_id = Column(
        UUID(as_uuid=True),
        ForeignKey("holatlar.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Holat ID"
    )
    foydalanuvchi_id = Column(
        UUID(as_uuid=True),
        ForeignKey("foydalanuvchilar.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Foydalanuvchi ID"
    )
    ota_izoh_id = Column(
        UUID(as_uuid=True),
        ForeignKey("holat_izohlari.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
        comment="Ota izoh ID (javob uchun)"
    )
    
    # Izoh matni
    matn = Column(
        Text,
        nullable=False,
        comment="Izoh matni"
    )
    
    # Statistika
    yoqtirishlar_soni = Column(
        Integer,
        default=0,
        nullable=False,
        comment="Yoqtirishlar soni"
    )
    javoblar_soni = Column(
        Integer,
        default=0,
        nullable=False,
        comment="Javoblar soni"
    )
    
    # Holat
    tahrirlangan = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="Tahrirlangan holati"
    )
    moderatsiya_holati = Column(
        String(20),
        default="tasdiqlangan",
        nullable=False,
        comment="Moderatsiya holati (kutilmoqda/tasdiqlangan/rad_etilgan)"
    )
    
    # Munosabatlar
    holat = relationship("Holat", back_populates="izohlar")
    foydalanuvchi = relationship("Foydalanuvchi", back_populates="izohlar")
    ota_izoh = relationship(
        "HolatIzohi",
        remote_side="HolatIzohi.id",
        back_populates="javoblar"
    )
    javoblar = relationship(
        "HolatIzohi",
        back_populates="ota_izoh",
        cascade="all, delete-orphan"
    )
    yoqtirishlar = relationship(
        "IzohYoqtirishi",
        back_populates="izoh",
        cascade="all, delete-orphan"
    )
    
    __table_args__ = (
        Index("idx_izoh_holat_vaqt", "holat_id", "yaratilgan_vaqt"),
        Index("idx_izoh_foydalanuvchi", "foydalanuvchi_id", "yaratilgan_vaqt"),
    )


class IzohYoqtirishi(AsosiyModel):
    """Izoh yoqtirishlari modeli (like)."""
    __tablename__ = "izoh_yoqtirishlari"
    
    izoh_id = Column(
        UUID(as_uuid=True),
        ForeignKey("holat_izohlari.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Izoh ID"
    )
    foydalanuvchi_id = Column(
        UUID(as_uuid=True),
        ForeignKey("foydalanuvchilar.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Foydalanuvchi ID"
    )
    
    izoh = relationship("HolatIzohi", back_populates="yoqtirishlar")
    foydalanuvchi = relationship("Foydalanuvchi")
    
    __table_args__ = (
        Index("idx_yoqtirish_unique", "izoh_id", "foydalanuvchi_id", unique=True),
    )
