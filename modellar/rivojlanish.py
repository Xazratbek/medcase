# MedCase Pro Platform - Rivojlanish Kuzatuvi Modellari
# Foydalanuvchi rivojlanishi, urinishlar va statistika

from sqlalchemy import (
    Column, String, Integer, ForeignKey, Text,
    Boolean, Float, DateTime, Date, Index, func
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from modellar.asosiy import AsosiyModel


class HolatUrinishi(AsosiyModel):
    """
    Holat urinishi modeli.
    Har bir foydalanuvchining har bir holatni yechish urinishi.
    """
    __tablename__ = "holat_urinishlari"
    
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
    sessiya_id = Column(
        UUID(as_uuid=True),
        ForeignKey("oqish_sessiyalari.id", ondelete="SET NULL"),
        nullable=True,
        comment="O'qish sessiyasi ID"
    )
    
    # Javob ma'lumotlari
    tanlangan_javob = Column(
        String(1),
        nullable=False,
        comment="Tanlangan javob (A, B, C, D)"
    )
    togri = Column(
        Boolean,
        nullable=False,
        index=True,
        comment="Javob to'g'riligi"
    )
    
    # Vaqt ma'lumotlari
    sarflangan_vaqt = Column(
        Integer,
        nullable=False,
        comment="Sarflangan vaqt (soniyalarda)"
    )
    boshlangan_vaqt = Column(
        DateTime(timezone=True),
        nullable=False,
        comment="Boshlangan vaqt"
    )
    tugallangan_vaqt = Column(
        DateTime(timezone=True),
        nullable=False,
        comment="Tugallangan vaqt"
    )
    
    # Ball
    olingan_ball = Column(
        Integer,
        default=0,
        nullable=False,
        comment="Olingan ball"
    )
    
    # Ko'rib chiqish
    korib_chiqilgan = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="Ko'rib chiqilgan holati"
    )
    korib_chiqish_vaqti = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="Ko'rib chiqish vaqti"
    )
    
    # Munosabatlar
    foydalanuvchi = relationship("Foydalanuvchi", back_populates="urinishlar")
    holat = relationship("Holat", back_populates="urinishlar")
    sessiya = relationship("OqishSessiyasi", back_populates="urinishlar")
    
    # Indekslar
    __table_args__ = (
        Index("idx_urinish_foyd_holat", "foydalanuvchi_id", "holat_id"),
        Index("idx_urinish_foyd_togri", "foydalanuvchi_id", "togri"),
        Index("idx_urinish_sana", "yaratilgan_vaqt"),
    )


class OqishSessiyasi(AsosiyModel):
    """
    O'qish sessiyasi modeli.
    Foydalanuvchining bir o'tirish davomidagi faoliyati.
    """
    __tablename__ = "oqish_sessiyalari"
    
    foydalanuvchi_id = Column(
        UUID(as_uuid=True),
        ForeignKey("foydalanuvchilar.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Foydalanuvchi ID"
    )
    
    # Vaqt
    boshlangan_vaqt = Column(
        DateTime(timezone=True),
        default=func.now(),
        nullable=False,
        comment="Sessiya boshlanish vaqti"
    )
    tugallangan_vaqt = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="Sessiya tugash vaqti"
    )
    davomiylik = Column(
        Integer,
        default=0,
        nullable=False,
        comment="Davomiylik (soniyalarda)"
    )
    
    # Statistika
    yechilgan_holatlar = Column(
        Integer,
        default=0,
        nullable=False,
        comment="Yechilgan holatlar soni"
    )
    togri_javoblar = Column(
        Integer,
        default=0,
        nullable=False,
        comment="To'g'ri javoblar soni"
    )
    olingan_ball = Column(
        Integer,
        default=0,
        nullable=False,
        comment="Olingan jami ball"
    )
    
    # Sessiya holati
    faol = Column(
        Boolean,
        default=True,
        nullable=False,
        index=True,
        comment="Sessiya faol holati"
    )
    
    # Qurilma ma'lumotlari
    qurilma_turi = Column(
        String(50),
        nullable=True,
        comment="Qurilma turi"
    )
    
    # Munosabatlar
    urinishlar = relationship(
        "HolatUrinishi",
        back_populates="sessiya"
    )
    
    # Indekslar
    __table_args__ = (
        Index("idx_sessiya_foyd_sana", "foydalanuvchi_id", "boshlangan_vaqt"),
    )


class KunlikStatistika(AsosiyModel):
    """
    Kunlik statistika modeli.
    Har bir foydalanuvchining kunlik rivojlanishi.
    """
    __tablename__ = "kunlik_statistika"
    
    foydalanuvchi_id = Column(
        UUID(as_uuid=True),
        ForeignKey("foydalanuvchilar.id", ondelete="CASCADE"),
        nullable=False,
        comment="Foydalanuvchi ID"
    )
    sana = Column(
        Date,
        nullable=False,
        index=True,
        comment="Sana"
    )
    
    # Asosiy statistika
    yechilgan_holatlar = Column(
        Integer,
        default=0,
        nullable=False,
        comment="Yechilgan holatlar"
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
    
    # Vaqt
    jami_vaqt = Column(
        Integer,
        default=0,
        nullable=False,
        comment="Jami sarflangan vaqt (soniyalarda)"
    )
    sessiyalar_soni = Column(
        Integer,
        default=0,
        nullable=False,
        comment="Sessiyalar soni"
    )
    
    # Ball
    olingan_ball = Column(
        Integer,
        default=0,
        nullable=False,
        comment="Olingan ball"
    )
    
    # Qiyinlik bo'yicha
    oson_yechilgan = Column(Integer, default=0, nullable=False)
    ortacha_yechilgan = Column(Integer, default=0, nullable=False)
    qiyin_yechilgan = Column(Integer, default=0, nullable=False)
    
    # Indekslar
    __table_args__ = (
        Index("idx_kunlik_foyd_sana", "foydalanuvchi_id", "sana", unique=True),
    )


class FoydalanuvchiRivojlanishi(AsosiyModel):
    """
    Foydalanuvchi umumiy rivojlanishi modeli.
    Barcha vaqt davomidagi jami statistika.
    """
    __tablename__ = "foydalanuvchi_rivojlanishi"
    
    foydalanuvchi_id = Column(
        UUID(as_uuid=True),
        ForeignKey("foydalanuvchilar.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        comment="Foydalanuvchi ID"
    )
    
    # Asosiy statistika
    jami_urinishlar = Column(
        Integer,
        default=0,
        nullable=False,
        comment="Jami urinishlar"
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
    
    # Foiz
    aniqlik_foizi = Column(
        Float,
        default=0.0,
        nullable=False,
        comment="Aniqlik foizi"
    )
    
    # Vaqt
    jami_vaqt = Column(
        Integer,
        default=0,
        nullable=False,
        comment="Jami o'qish vaqti (soniyalarda)"
    )
    ortacha_vaqt = Column(
        Float,
        default=0.0,
        nullable=False,
        comment="O'rtacha vaqt per holat"
    )
    
    # Streak
    joriy_streak = Column(
        Integer,
        default=0,
        nullable=False,
        comment="Joriy streak (ketma-ket kunlar)"
    )
    eng_uzun_streak = Column(
        Integer,
        default=0,
        nullable=False,
        comment="Eng uzun streak"
    )
    oxirgi_faollik = Column(
        Date,
        nullable=True,
        comment="Oxirgi faollik sanasi"
    )
    
    # Level va ball
    daraja = Column(
        Integer,
        default=1,
        nullable=False,
        index=True,
        comment="Foydalanuvchi darajasi"
    )
    jami_ball = Column(
        Integer,
        default=0,
        nullable=False,
        index=True,
        comment="Jami ball"
    )
    
    # Qiyinlik bo'yicha statistika
    oson_yechilgan = Column(Integer, default=0, nullable=False)
    oson_togri = Column(Integer, default=0, nullable=False)
    ortacha_yechilgan = Column(Integer, default=0, nullable=False)
    ortacha_togri = Column(Integer, default=0, nullable=False)
    qiyin_yechilgan = Column(Integer, default=0, nullable=False)
    qiyin_togri = Column(Integer, default=0, nullable=False)
    
    # Kategoriya bo'yicha statistika (JSONB)
    kategoriya_statistikasi = Column(
        JSONB,
        default={},
        nullable=False,
        comment="Kategoriya bo'yicha statistika"
    )
    
    # Kuchli va zaif tomonlar
    kuchli_tomonlar = Column(
        JSONB,
        default=[],
        nullable=False,
        comment="Kuchli tomonlar ro'yxati"
    )
    zaif_tomonlar = Column(
        JSONB,
        default=[],
        nullable=False,
        comment="Zaif tomonlar ro'yxati"
    )
    
    # Munosabatlar
    foydalanuvchi = relationship(
        "Foydalanuvchi",
        back_populates="rivojlanish"
    )
    
    @property
    def aniqlik_hisoblash(self) -> float:
        """Aniqlik foizini hisoblaydi."""
        if self.jami_urinishlar == 0:
            return 0.0
        return (self.togri_javoblar / self.jami_urinishlar) * 100


class BolimRivojlanishi(AsosiyModel):
    """
    Bo'lim bo'yicha rivojlanish modeli.
    Har bir bo'lim uchun alohida statistika.
    """
    __tablename__ = "bolim_rivojlanishi"
    
    foydalanuvchi_id = Column(
        UUID(as_uuid=True),
        ForeignKey("foydalanuvchilar.id", ondelete="CASCADE"),
        nullable=False,
        comment="Foydalanuvchi ID"
    )
    bolim_id = Column(
        UUID(as_uuid=True),
        ForeignKey("bolimlar.id", ondelete="CASCADE"),
        nullable=False,
        comment="Bo'lim ID"
    )
    
    # Statistika
    jami_holatlar = Column(Integer, default=0, nullable=False)
    yechilgan_holatlar = Column(Integer, default=0, nullable=False)
    togri_javoblar = Column(Integer, default=0, nullable=False)
    aniqlik_foizi = Column(Float, default=0.0, nullable=False)
    jami_vaqt = Column(Integer, default=0, nullable=False)
    
    # Tugallash holati
    tugallangan = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="Bo'lim tugallangan"
    )
    tugallangan_vaqt = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="Tugallangan vaqt"
    )
    
    # Indekslar
    __table_args__ = (
        Index("idx_bolim_riv_foyd_bolim", "foydalanuvchi_id", "bolim_id", unique=True),
    )
