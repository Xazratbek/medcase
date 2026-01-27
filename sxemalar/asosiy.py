# MedCase Pro Platform - Asosiy Sxemalar
# Barcha sxemalar uchun bazaviy klasslar

from pydantic import BaseModel, Field, ConfigDict
from typing import TypeVar, Generic, List, Optional, Any
from datetime import datetime
from uuid import UUID

T = TypeVar("T")


class AsosiySchema(BaseModel):
    """Barcha sxemalar uchun asosiy klass."""
    
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        json_encoders={
            datetime: lambda v: v.isoformat() if v else None,
            UUID: lambda v: str(v) if v else None
        }
    )


class VaqtBelgilariSchema(AsosiySchema):
    """Vaqt belgilari bilan sxema."""
    yaratilgan_vaqt: datetime = Field(..., description="Yaratilgan vaqt")
    yangilangan_vaqt: datetime = Field(..., description="Yangilangan vaqt")


class IDliSchema(AsosiySchema):
    """ID bilan sxema."""
    id: UUID = Field(..., description="Unikal identifikator")


class SahifalashSchema(AsosiySchema):
    """Sahifalash parametrlari."""
    sahifa: int = Field(default=1, ge=1, description="Sahifa raqami")
    hajm: int = Field(default=20, ge=1, le=100, description="Sahifa hajmi")
    
    @property
    def offset(self) -> int:
        """Offset hisoblash."""
        return (self.sahifa - 1) * self.hajm


class SahifalanganJavob(AsosiySchema, Generic[T]):
    """Sahifalangan javob."""
    elementlar: List[T] = Field(..., description="Elementlar ro'yxati")
    jami: int = Field(..., description="Jami elementlar soni")
    sahifa: int = Field(..., description="Joriy sahifa")
    hajm: int = Field(..., description="Sahifa hajmi")
    sahifalar_soni: int = Field(..., description="Jami sahifalar soni")
    
    @classmethod
    def yaratish(
        cls,
        elementlar: List[T],
        jami: int,
        sahifa: int,
        hajm: int
    ) -> "SahifalanganJavob[T]":
        """Sahifalangan javob yaratish."""
        sahifalar_soni = (jami + hajm - 1) // hajm if hajm > 0 else 0
        return cls(
            elementlar=elementlar,
            jami=jami,
            sahifa=sahifa,
            hajm=hajm,
            sahifalar_soni=sahifalar_soni
        )


class MuvaffaqiyatJavob(AsosiySchema):
    """Muvaffaqiyatli javob."""
    muvaffaqiyat: bool = Field(default=True, description="Muvaffaqiyat holati")
    xabar: str = Field(..., description="Javob xabari")
    malumot: Optional[Any] = Field(default=None, description="Qo'shimcha ma'lumot")


class XatoJavob(AsosiySchema):
    """Xato javobi."""
    muvaffaqiyat: bool = Field(default=False, description="Muvaffaqiyat holati")
    xato: str = Field(..., description="Xato xabari")
    xato_kodi: str = Field(..., description="Xato kodi")
    tafsilotlar: Optional[Any] = Field(default=None, description="Xato tafsilotlari")


class TartibOzgartirish(AsosiySchema):
    """Tartib o'zgartirish uchun sxema."""
    id: UUID = Field(..., description="Element ID")
    tartib: int = Field(..., ge=0, description="Yangi tartib")


class OmmaviYozuvJavob(AsosiySchema):
    """Ommaviy yozuv operatsiyasi javobi."""
    muvaffaqiyatli: int = Field(..., description="Muvaffaqiyatli yozuvlar soni")
    xatoli: int = Field(..., description="Xatoli yozuvlar soni")
    xatolar: List[str] = Field(default=[], description="Xato xabarlari")
