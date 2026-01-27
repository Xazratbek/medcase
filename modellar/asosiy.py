# MedCase Pro Platform - Asosiy Model
# Barcha modellar uchun umumiy bazaviy klass

from sqlalchemy import Column, DateTime, Boolean, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declared_attr
from datetime import datetime
import uuid

from sozlamalar.malumotlar_bazasi import Base


class VaqtBelgilari:
    """Vaqt belgilari mixin - yaratilgan va yangilangan vaqtlar."""
    
    @declared_attr
    def yaratilgan_vaqt(cls):
        return Column(
            DateTime(timezone=True),
            default=func.now(),
            nullable=False,
            index=True,
            comment="Yozuv yaratilgan vaqt"
        )
    
    @declared_attr
    def yangilangan_vaqt(cls):
        return Column(
            DateTime(timezone=True),
            default=func.now(),
            onupdate=func.now(),
            nullable=False,
            comment="Yozuv oxirgi yangilangan vaqt"
        )


class AsosiyModel(Base, VaqtBelgilari):
    """
    Barcha modellar uchun asosiy klass.
    UUID primary key va vaqt belgilarini o'z ichiga oladi.
    """
    __abstract__ = True
    
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
        comment="Unikal identifikator"
    )
    
    faol = Column(
        Boolean,
        default=True,
        nullable=False,
        index=True,
        comment="Yozuv faol holati"
    )
    
    def __repr__(self):
        return f"<{self.__class__.__name__}(id={self.id})>"
    
    def dict_ga(self) -> dict:
        """Modelni dictionary formatiga o'zgartiradi."""
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }
    
    @classmethod
    def jadval_nomi(cls) -> str:
        """Jadval nomini qaytaradi."""
        return cls.__tablename__
