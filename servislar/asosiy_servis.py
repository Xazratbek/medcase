# MedCase Pro Platform - Asosiy Servis
# Barcha servislar uchun bazaviy klass

from typing import TypeVar, Generic, Optional, List, Type, Any
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func, and_
from sqlalchemy.orm import selectinload

from modellar.asosiy import AsosiyModel

ModelType = TypeVar("ModelType", bound=AsosiyModel)


class AsosiyServis(Generic[ModelType]):
    """
    Barcha servislar uchun asosiy CRUD operatsiyalari.
    Generic pattern yordamida har qanday model uchun ishlatiladi.
    """
    
    def __init__(self, model: Type[ModelType], db: AsyncSession):
        self.model = model
        self.db = db
    
    async def yaratish(self, **malumotlar) -> ModelType:
        """Yangi yozuv yaratadi."""
        ob = self.model(**malumotlar)
        self.db.add(ob)
        await self.db.flush()
        await self.db.refresh(ob)
        return ob
    
    async def id_bilan_olish(
        self,
        id: UUID,
        yuklamalar: List[str] = None
    ) -> Optional[ModelType]:
        """ID bo'yicha yozuv oladi."""
        sorov = select(self.model).where(self.model.id == id)
        
        if yuklamalar:
            for yuklama in yuklamalar:
                sorov = sorov.options(selectinload(getattr(self.model, yuklama)))
        
        natija = await self.db.execute(sorov)
        return natija.scalar_one_or_none()
    
    async def hammasi(
        self,
        sahifa: int = 1,
        hajm: int = 20,
        faol_faqat: bool = True,
        saralash: str = "yaratilgan_vaqt",
        tartib: str = "desc",
        yuklamalar: List[str] = None
    ) -> tuple[List[ModelType], int]:
        """Barcha yozuvlarni sahifalab oladi."""
        # Asosiy sorov
        sorov = select(self.model)
        hisob_sorov = select(func.count(self.model.id))
        
        # Faol filter
        if faol_faqat and hasattr(self.model, "faol"):
            sorov = sorov.where(self.model.faol == True)
            hisob_sorov = hisob_sorov.where(self.model.faol == True)
        
        # Yuklamalar
        if yuklamalar:
            for yuklama in yuklamalar:
                sorov = sorov.options(selectinload(getattr(self.model, yuklama)))
        
        # Saralash
        saralash_maydoni = getattr(self.model, saralash, self.model.yaratilgan_vaqt)
        if tartib == "desc":
            sorov = sorov.order_by(saralash_maydoni.desc())
        else:
            sorov = sorov.order_by(saralash_maydoni.asc())
        
        # Sahifalash
        offset = (sahifa - 1) * hajm
        sorov = sorov.offset(offset).limit(hajm)
        
        # Bajarish
        natija = await self.db.execute(sorov)
        jami = await self.db.execute(hisob_sorov)
        
        return natija.scalars().all(), jami.scalar()
    
    async def yangilash(
        self,
        id: UUID,
        **malumotlar
    ) -> Optional[ModelType]:
        """Yozuvni yangilaydi."""
        # Bo'sh qiymatlarni olib tashlash
        malumotlar = {k: v for k, v in malumotlar.items() if v is not None}
        
        if not malumotlar:
            return await self.id_bilan_olish(id)
        
        sorov = (
            update(self.model)
            .where(self.model.id == id)
            .values(**malumotlar)
            .returning(self.model)
        )
        natija = await self.db.execute(sorov)
        await self.db.flush()
        
        return await self.id_bilan_olish(id)
    
    async def ochirish(self, id: UUID, yumshoq: bool = True) -> bool:
        """
        Yozuvni o'chiradi.
        yumshoq=True bo'lsa, faqat faol=False qiladi.
        """
        if yumshoq and hasattr(self.model, "faol"):
            sorov = (
                update(self.model)
                .where(self.model.id == id)
                .values(faol=False)
            )
        else:
            sorov = delete(self.model).where(self.model.id == id)
        
        natija = await self.db.execute(sorov)
        await self.db.flush()
        return natija.rowcount > 0
    
    async def mavjud(self, id: UUID) -> bool:
        """Yozuv mavjudligini tekshiradi."""
        sorov = select(func.count(self.model.id)).where(self.model.id == id)
        natija = await self.db.execute(sorov)
        return natija.scalar() > 0
    
    async def soni(self, faol_faqat: bool = True) -> int:
        """Yozuvlar sonini qaytaradi."""
        sorov = select(func.count(self.model.id))
        if faol_faqat and hasattr(self.model, "faol"):
            sorov = sorov.where(self.model.faol == True)
        natija = await self.db.execute(sorov)
        return natija.scalar()
    
    async def maydon_bilan_olish(
        self,
        maydon: str,
        qiymat: Any
    ) -> Optional[ModelType]:
        """Ma'lum maydon qiymati bo'yicha oladi."""
        maydon_attr = getattr(self.model, maydon, None)
        if maydon_attr is None:
            return None
        
        sorov = select(self.model).where(maydon_attr == qiymat)
        natija = await self.db.execute(sorov)
        return natija.scalar_one_or_none()
    
    async def koplab_yaratish(self, royxat: List[dict]) -> List[ModelType]:
        """Bir nechta yozuv yaratadi."""
        oblar = [self.model(**m) for m in royxat]
        self.db.add_all(oblar)
        await self.db.flush()
        return oblar
