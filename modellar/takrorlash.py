# MedCase Pro Platform - Spaced Repetition (SM-2) Modellari
# SuperMemo SM-2 algoritmi bilan takrorlash tizimi

from sqlalchemy import (
    Column, String, Integer, ForeignKey, Float,
    Boolean, DateTime, Date, Index, func
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime, date, timedelta

from modellar.asosiy import AsosiyModel


class TakrorlashKartasi(AsosiyModel):
    """
    Spaced Repetition kartasi (SM-2 algoritmi).
    Har bir foydalanuvchi-holat juftligi uchun takrorlash ma'lumotlari.
    """
    __tablename__ = "takrorlash_kartalari"
    
    # Bog'lanishlar
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
    
    # SM-2 parametrlari
    easiness_factor = Column(
        Float,
        default=2.5,
        nullable=False,
        comment="Osonlik faktori (EF) - 1.3 dan 2.5 gacha"
    )
    interval = Column(
        Integer,
        default=1,
        nullable=False,
        comment="Joriy interval (kunlarda)"
    )
    repetition = Column(
        Integer,
        default=0,
        nullable=False,
        comment="Takrorlashlar soni"
    )
    
    # Sanalar
    oxirgi_takrorlash = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="Oxirgi takrorlash vaqti"
    )
    keyingi_takrorlash = Column(
        Date,
        nullable=False,
        default=date.today,
        index=True,
        comment="Keyingi takrorlash sanasi"
    )
    
    # Statistika
    jami_takrorlashlar = Column(
        Integer,
        default=0,
        nullable=False,
        comment="Jami takrorlashlar soni"
    )
    togri_javoblar = Column(
        Integer,
        default=0,
        nullable=False,
        comment="To'g'ri javoblar soni"
    )
    
    # Holat
    oqilgan = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="O'qilgan/o'rganilgan deb belgilangan"
    )
    
    # Munosabatlar
    foydalanuvchi = relationship("Foydalanuvchi", back_populates="takrorlash_kartalari")
    holat = relationship("Holat", back_populates="takrorlash_kartalari")
    tarix = relationship(
        "TakrorlashTarixi",
        back_populates="karta",
        cascade="all, delete-orphan",
        order_by="TakrorlashTarixi.yaratilgan_vaqt.desc()"
    )
    
    __table_args__ = (
        Index("idx_takrorlash_foydalanuvchi_holat", "foydalanuvchi_id", "holat_id", unique=True),
        Index("idx_takrorlash_keyingi", "foydalanuvchi_id", "keyingi_takrorlash"),
    )
    
    def sm2_hisoblash(self, sifat: int) -> None:
        """
        SM-2 algoritmini qo'llash.
        
        sifat: 0-5 oralig'ida baho
            0 - Umuman eslolmadim
            1 - Noto'g'ri, lekin to'g'ri javobni ko'rganda esladim
            2 - Noto'g'ri, lekin to'g'ri javob juda tanish
            3 - To'g'ri, lekin qiyin bo'ldi
            4 - To'g'ri, biroz o'ylab topdim
            5 - To'g'ri, oson
        """
        # EF yangilash
        self.easiness_factor = max(
            1.3,
            self.easiness_factor + (0.1 - (5 - sifat) * (0.08 + (5 - sifat) * 0.02))
        )
        
        if sifat < 3:
            # Noto'g'ri javob - qaytadan boshlash
            self.repetition = 0
            self.interval = 1
        else:
            # To'g'ri javob
            self.togri_javoblar += 1
            if self.repetition == 0:
                self.interval = 1
            elif self.repetition == 1:
                self.interval = 6
            else:
                self.interval = round(self.interval * self.easiness_factor)
            self.repetition += 1
        
        self.jami_takrorlashlar += 1
        self.oxirgi_takrorlash = datetime.utcnow()
        self.keyingi_takrorlash = date.today() + timedelta(days=self.interval)
    
    @property
    def aniqlik_foizi(self) -> float:
        """Aniqlik foizini hisoblash."""
        if self.jami_takrorlashlar == 0:
            return 0.0
        return (self.togri_javoblar / self.jami_takrorlashlar) * 100


class TakrorlashTarixi(AsosiyModel):
    """Takrorlash tarixi - har bir takrorlash yozuvi."""
    __tablename__ = "takrorlash_tarixi"
    
    karta_id = Column(
        UUID(as_uuid=True),
        ForeignKey("takrorlash_kartalari.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Karta ID"
    )
    
    # Natija
    sifat = Column(
        Integer,
        nullable=False,
        comment="Sifat bahosi (0-5)"
    )
    togri = Column(
        Boolean,
        nullable=False,
        comment="To'g'ri javob"
    )
    sarflangan_vaqt = Column(
        Integer,
        nullable=True,
        comment="Sarflangan vaqt (soniyalarda)"
    )
    
    # SM-2 qiymatlari shu paytda
    ef_oldin = Column(Float, comment="EF oldingi qiymat")
    ef_keyin = Column(Float, comment="EF yangi qiymat")
    interval_oldin = Column(Integer, comment="Interval oldingi")
    interval_keyin = Column(Integer, comment="Interval yangi")
    
    karta = relationship("TakrorlashKartasi", back_populates="tarix")
    
    __table_args__ = (
        Index("idx_tarix_karta_vaqt", "karta_id", "yaratilgan_vaqt"),
    )


class TakrorlashSessiyasi(AsosiyModel):
    """Takrorlash sessiyasi - bir martalik o'qish sessiyasi."""
    __tablename__ = "takrorlash_sessiyalari"
    
    foydalanuvchi_id = Column(
        UUID(as_uuid=True),
        ForeignKey("foydalanuvchilar.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Foydalanuvchi ID"
    )
    
    # Sessiya ma'lumotlari
    boshlangan_vaqt = Column(
        DateTime(timezone=True),
        default=func.now(),
        nullable=False,
        comment="Boshlangan vaqt"
    )
    tugallangan_vaqt = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="Tugallangan vaqt"
    )
    
    # Statistika
    jami_kartalar = Column(
        Integer,
        default=0,
        nullable=False,
        comment="Jami kartalar soni"
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
    
    # Reja
    reja_kartalar = Column(
        Integer,
        default=20,
        nullable=False,
        comment="Rejadagi kartalar soni"
    )
    
    foydalanuvchi = relationship("Foydalanuvchi")
