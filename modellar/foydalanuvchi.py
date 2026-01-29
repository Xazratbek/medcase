# MedCase Pro Platform - Foydalanuvchi Modellari
# Foydalanuvchi, profil, sessiya va OAuth modellari

from sqlalchemy import (
    Column, String, Boolean, Integer, ForeignKey,
    Text, DateTime, Enum as SQLEnum, Index, func
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from modellar.asosiy import AsosiyModel


class FoydalanuvchiRoli(str, enum.Enum):
    """Foydalanuvchi rollari."""
    TALABA = "talaba"
    REZIDENT = "rezident"
    SHIFOKOR = "shifokor"
    OQITUVCHI = "oqituvchi"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"


class Foydalanuvchi(AsosiyModel):
    """
    Foydalanuvchi modeli.
    Tizimga kirish va autentifikatsiya uchun asosiy model.
    """
    __tablename__ = "foydalanuvchilar"
    
    # Asosiy maydonlar
    email = Column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
        comment="Foydalanuvchi email manzili"
    )
    foydalanuvchi_nomi = Column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
        comment="Unikal foydalanuvchi nomi"
    )
    parol_hash = Column(
        String(255),
        nullable=False,
        comment="Shifrlangan parol"
    )
    
    # Shaxsiy ma'lumotlar
    ism = Column(
        String(100),
        nullable=False,
        comment="Foydalanuvchi ismi"
    )
    familiya = Column(
        String(100),
        nullable=False,
        comment="Foydalanuvchi familiyasi"
    )
    
    # Rol va holat
    rol = Column(
        SQLEnum(FoydalanuvchiRoli),
        default=FoydalanuvchiRoli.TALABA,
        nullable=False,
        index=True,
        comment="Foydalanuvchi roli"
    )
    email_tasdiqlangan = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="Email tasdiqlangan holati"
    )
    
    # Oxirgi faollik
    oxirgi_kirish = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="Oxirgi kirish vaqti"
    )
    
    # Munosabatlar
    profil = relationship(
        "FoydalanuvchiProfili",
        back_populates="foydalanuvchi",
        uselist=False,
        cascade="all, delete-orphan"
    )
    sessiyalar = relationship(
        "FoydalanuvchiSessiyasi",
        back_populates="foydalanuvchi",
        cascade="all, delete-orphan"
    )
    oauth_hisoblar = relationship(
        "OAuthHisob",
        back_populates="foydalanuvchi",
        cascade="all, delete-orphan"
    )
    urinishlar = relationship(
        "HolatUrinishi",
        back_populates="foydalanuvchi",
        cascade="all, delete-orphan"
    )
    rivojlanish = relationship(
        "FoydalanuvchiRivojlanishi",
        back_populates="foydalanuvchi",
        uselist=False,
        cascade="all, delete-orphan"
    )
    nishonlar = relationship(
        "FoydalanuvchiNishoni",
        back_populates="foydalanuvchi",
        cascade="all, delete-orphan"
    )
    balllar = relationship(
        "Ball",
        back_populates="foydalanuvchi",
        cascade="all, delete-orphan"
    )
    xatcholar = relationship(
        "Xatcho",
        back_populates="foydalanuvchi",
        cascade="all, delete-orphan"
    )
    eslatmalar = relationship(
        "Eslatma",
        back_populates="foydalanuvchi",
        cascade="all, delete-orphan"
    )
    obuna = relationship(
        "Obuna",
        back_populates="foydalanuvchi",
        uselist=False,
        cascade="all, delete-orphan"
    )
    bildirishnomalar = relationship(
        "Bildirishnoma",
        back_populates="foydalanuvchi",
        cascade="all, delete-orphan"
    )
    push_obunalar = relationship(
        "PushObuna",
        back_populates="foydalanuvchi",
        cascade="all, delete-orphan"
    )
    izohlar = relationship(
        "HolatIzohi",
        back_populates="foydalanuvchi",
        cascade="all, delete-orphan"
    )
    takrorlash_kartalari = relationship(
        "TakrorlashKartasi",
        back_populates="foydalanuvchi",
        cascade="all, delete-orphan"
    )
    imtihonlar = relationship(
        "Imtihon",
        back_populates="foydalanuvchi",
        cascade="all, delete-orphan"
    )
    
    # Indekslar
    __table_args__ = (
        Index("idx_foydalanuvchi_email_faol", "email", "faol"),
        Index("idx_foydalanuvchi_rol_faol", "rol", "faol"),
    )
    
    @property
    def toliq_ism(self) -> str:
        """To'liq ismni qaytaradi."""
        return f"{self.ism} {self.familiya}"
    
    @property
    def admin_ekanligini_tekshirish(self) -> bool:
        """Admin ekanligini tekshiradi."""
        return self.rol in [FoydalanuvchiRoli.ADMIN, FoydalanuvchiRoli.SUPER_ADMIN]


class FoydalanuvchiProfili(AsosiyModel):
    """
    Foydalanuvchi profili modeli.
    Qo'shimcha ma'lumotlar va sozlamalar.
    """
    __tablename__ = "foydalanuvchi_profillari"
    
    # Foydalanuvchi bog'lanishi
    foydalanuvchi_id = Column(
        UUID(as_uuid=True),
        ForeignKey("foydalanuvchilar.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        comment="Foydalanuvchi ID"
    )
    
    # Avatar va rasm
    avatar_url = Column(
        String(500),
        nullable=True,
        comment="Avatar rasm URL"
    )
    
    # Ta'lim ma'lumotlari
    muassasa = Column(
        String(255),
        nullable=True,
        comment="O'quv muassasasi nomi"
    )
    mutaxassislik = Column(
        String(255),
        nullable=True,
        comment="Mutaxassislik yo'nalishi"
    )
    kurs_yili = Column(
        Integer,
        nullable=True,
        comment="Kurs yili (1-6)"
    )
    
    # Bio va ijtimoiy
    bio = Column(
        Text,
        nullable=True,
        comment="Qisqacha tavsif"
    )
    telefon = Column(
        String(20),
        nullable=True,
        comment="Telefon raqami"
    )
    shahar = Column(
        String(100),
        nullable=True,
        comment="Shahar"
    )
    mamlakat = Column(
        String(100),
        default="O'zbekiston",
        nullable=True,
        comment="Mamlakat"
    )
    
    # Sozlamalar
    til = Column(
        String(10),
        default="uz",
        nullable=False,
        comment="Interfeys tili"
    )
    mavzu = Column(
        String(20),
        default="yorug",
        nullable=False,
        comment="Interfeys mavzusi (yorug/qorong'i)"
    )
    
    # Kunlik maqsadlar
    kunlik_maqsad = Column(
        Integer,
        default=10,
        nullable=False,
        comment="Kunlik yechish kerak bo'lgan holatlar soni"
    )
    
    # Maxfiylik sozlamalari
    profil_ochiq = Column(
        Boolean,
        default=True,
        nullable=False,
        comment="Profil boshqalarga ko'rinadi"
    )
    reytingda_korsatish = Column(
        Boolean,
        default=True,
        nullable=False,
        comment="Reytingda ko'rsatish"
    )
    
    # Qo'shimcha sozlamalar (JSONB)
    qoshimcha_sozlamalar = Column(
        JSONB,
        default={},
        nullable=False,
        comment="Qo'shimcha sozlamalar"
    )
    
    # Munosabatlar
    foydalanuvchi = relationship(
        "Foydalanuvchi",
        back_populates="profil"
    )


class FoydalanuvchiSessiyasi(AsosiyModel):
    """
    Foydalanuvchi sessiyalari modeli.
    Ko'p qurilmadan kirish va sessiya boshqaruvi.
    """
    __tablename__ = "foydalanuvchi_sessiyalari"
    
    foydalanuvchi_id = Column(
        UUID(as_uuid=True),
        ForeignKey("foydalanuvchilar.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Foydalanuvchi ID"
    )
    
    # Token ma'lumotlari
    yangilash_token = Column(
        String(500),
        unique=True,
        nullable=False,
        comment="Yangilash tokeni"
    )
    token_hash = Column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
        comment="Token hash"
    )
    
    # Qurilma ma'lumotlari
    qurilma_turi = Column(
        String(50),
        nullable=True,
        comment="Qurilma turi (mobil/desktop/tablet)"
    )
    qurilma_nomi = Column(
        String(500),
        nullable=True,
        comment="Qurilma nomi"
    )
    brauzer = Column(
        String(500),
        nullable=True,
        comment="Brauzer nomi (User-Agent)"
    )
    operatsion_tizim = Column(
        String(100),
        nullable=True,
        comment="Operatsion tizim"
    )
    ip_manzil = Column(
        String(45),
        nullable=True,
        comment="IP manzil"
    )
    
    # Vaqtlar
    amal_qilish_vaqti = Column(
        DateTime(timezone=True),
        nullable=False,
        comment="Token amal qilish muddati"
    )
    oxirgi_faollik = Column(
        DateTime(timezone=True),
        default=func.now(),
        nullable=False,
        comment="Oxirgi faollik vaqti"
    )
    
    # Munosabatlar
    foydalanuvchi = relationship(
        "Foydalanuvchi",
        back_populates="sessiyalar"
    )
    
    # Indekslar
    __table_args__ = (
        Index("idx_sessiya_foydalanuvchi_faol", "foydalanuvchi_id", "faol"),
        Index("idx_sessiya_amal_qilish", "amal_qilish_vaqti"),
    )


class OAuthHisob(AsosiyModel):
    """
    OAuth hisoblar modeli.
    Google, Microsoft va boshqa provayderlar orqali kirish.
    """
    __tablename__ = "oauth_hisoblar"
    
    foydalanuvchi_id = Column(
        UUID(as_uuid=True),
        ForeignKey("foydalanuvchilar.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Foydalanuvchi ID"
    )
    
    # OAuth ma'lumotlari
    provayder = Column(
        String(50),
        nullable=False,
        comment="OAuth provayder (google/microsoft)"
    )
    provayder_foydalanuvchi_id = Column(
        String(255),
        nullable=False,
        comment="Provayderda foydalanuvchi ID"
    )
    
    # Tokenlar
    kirish_tokeni = Column(
        Text,
        nullable=True,
        comment="Kirish tokeni"
    )
    yangilash_tokeni = Column(
        Text,
        nullable=True,
        comment="Yangilash tokeni"
    )
    token_amal_qilish_vaqti = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="Token amal qilish muddati"
    )
    
    # Munosabatlar
    foydalanuvchi = relationship(
        "Foydalanuvchi",
        back_populates="oauth_hisoblar"
    )
    
    # Indekslar
    __table_args__ = (
        Index(
            "idx_oauth_provayder_id",
            "provayder",
            "provayder_foydalanuvchi_id",
            unique=True
        ),
    )
