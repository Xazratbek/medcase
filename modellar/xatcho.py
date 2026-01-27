# MedCase Pro Platform - Xatcho va Eslatma Modellari
# Foydalanuvchi xatcholari va eslatmalari

from sqlalchemy import (
    Column, String, Integer, ForeignKey, Text,
    DateTime, Index
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from modellar.asosiy import AsosiyModel


class XatchoJildi(AsosiyModel):
    """Xatcho jildlari modeli."""
    __tablename__ = "xatcho_jildlari"
    
    foydalanuvchi_id = Column(
        UUID(as_uuid=True),
        ForeignKey("foydalanuvchilar.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Foydalanuvchi ID"
    )
    
    nom = Column(
        String(100),
        nullable=False,
        comment="Jild nomi"
    )
    tavsif = Column(
        Text,
        nullable=True,
        comment="Jild tavsifi"
    )
    rang = Column(
        String(7),
        default="#3B82F6",
        nullable=False,
        comment="Jild rangi"
    )
    tartib = Column(
        Integer,
        default=0,
        nullable=False,
        comment="Tartib"
    )
    
    # Statistika
    xatcholar_soni = Column(
        Integer,
        default=0,
        nullable=False,
        comment="Xatcholar soni"
    )
    
    xatcholar = relationship(
        "Xatcho",
        back_populates="jild",
        cascade="all, delete-orphan"
    )


class Xatcho(AsosiyModel):
    """Xatcho (Bookmark) modeli."""
    __tablename__ = "xatcholar"
    
    foydalanuvchi_id = Column(
        UUID(as_uuid=True),
        ForeignKey("foydalanuvchilar.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Foydalanuvchi ID"
    )
    holat_id = Column(
        UUID(as_uuid=True),
        ForeignKey("holatlar.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Holat ID"
    )
    jild_id = Column(
        UUID(as_uuid=True),
        ForeignKey("xatcho_jildlari.id", ondelete="SET NULL"),
        nullable=True,
        comment="Jild ID"
    )
    
    eslatma = Column(
        Text,
        nullable=True,
        comment="Qisqa eslatma"
    )
    
    foydalanuvchi = relationship("Foydalanuvchi", back_populates="xatcholar")
    jild = relationship("XatchoJildi", back_populates="xatcholar")
    
    __table_args__ = (
        Index("idx_xatcho_foyd_holat", "foydalanuvchi_id", "holat_id", unique=True),
    )


class Eslatma(AsosiyModel):
    """Foydalanuvchi eslatmalari modeli."""
    __tablename__ = "eslatmalar"
    
    foydalanuvchi_id = Column(
        UUID(as_uuid=True),
        ForeignKey("foydalanuvchilar.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Foydalanuvchi ID"
    )
    holat_id = Column(
        UUID(as_uuid=True),
        ForeignKey("holatlar.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Holat ID"
    )
    
    sarlavha = Column(
        String(255),
        nullable=True,
        comment="Eslatma sarlavhasi"
    )
    matn = Column(
        Text,
        nullable=False,
        comment="Eslatma matni"
    )
    
    foydalanuvchi = relationship("Foydalanuvchi", back_populates="eslatmalar")
    
    __table_args__ = (
        Index("idx_eslatma_foyd_holat", "foydalanuvchi_id", "holat_id"),
    )
