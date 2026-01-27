# MedCase Pro Platform - Izoh Sxemalari
# Forum/Izohlar uchun Pydantic sxemalari

from pydantic import Field
from typing import Optional, List
from uuid import UUID
from datetime import datetime

from sxemalar.asosiy import AsosiySchema, IDliSchema, VaqtBelgilariSchema


class IzohYaratish(AsosiySchema):
    """Izoh yaratish."""
    holat_id: UUID = Field(..., description="Holat ID")
    matn: str = Field(..., min_length=1, max_length=5000, description="Izoh matni")
    ota_izoh_id: Optional[UUID] = Field(None, description="Ota izoh ID (javob uchun)")


class IzohYangilash(AsosiySchema):
    """Izoh yangilash."""
    matn: str = Field(..., min_length=1, max_length=5000, description="Yangi matn")


class IzohFoydalanuvchi(AsosiySchema):
    """Izoh uchun foydalanuvchi ma'lumotlari."""
    id: UUID
    foydalanuvchi_nomi: str
    ism: str
    familiya: str
    avatar_url: Optional[str] = None


class IzohJavob(IDliSchema, VaqtBelgilariSchema):
    """Izoh javobi."""
    holat_id: UUID
    foydalanuvchi_id: UUID
    foydalanuvchi: Optional[IzohFoydalanuvchi] = None
    ota_izoh_id: Optional[UUID] = None
    matn: str
    yoqtirishlar_soni: int = 0
    javoblar_soni: int = 0
    tahrirlangan: bool = False
    yoqtirilgan: bool = False  # Joriy foydalanuvchi yoqtirganmi
    javoblar: List["IzohJavob"] = []


class IzohlarRoyxati(AsosiySchema):
    """Izohlar ro'yxati."""
    izohlar: List[IzohJavob] = []
    jami: int = 0
    sahifa: int = 1
    hajm: int = 20
    sahifalar_soni: int = 0


class YoqtirishJavob(AsosiySchema):
    """Yoqtirish javobi."""
    yoqtirilgan: bool
    yoqtirishlar_soni: int


# Forward reference uchun
IzohJavob.model_rebuild()
