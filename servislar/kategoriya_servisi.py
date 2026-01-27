# MedCase Pro Platform - Kategoriya Servisi
# Kategoriyalar, kichik kategoriyalar va bo'limlar boshqaruvi

from typing import Optional, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload

from servislar.asosiy_servis import AsosiyServis
from modellar.kategoriya import AsosiyKategoriya, KichikKategoriya, Bolim
from sxemalar.kategoriya import (
    AsosiyKategoriyaYaratish,
    KichikKategoriyaYaratish,
    BolimYaratish
)
from sozlamalar.redis_kesh import redis_kesh, kesh_dekoratori, KeshKalitlari


class KategoriyaServisi:
    """Kategoriyalar boshqaruvi servisi."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self._asosiy = AsosiyServis(AsosiyKategoriya, db)
        self._kichik = AsosiyServis(KichikKategoriya, db)
        self._bolim = AsosiyServis(Bolim, db)
    
    # ============== Asosiy Kategoriya ==============
    
    async def asosiy_kategoriya_yaratish(
        self,
        malumot: AsosiyKategoriyaYaratish
    ) -> AsosiyKategoriya:
        """Asosiy kategoriya yaratadi."""
        kategoriya = await self._asosiy.yaratish(**malumot.model_dump())
        await redis_kesh.shablon_ochirish(f"{KeshKalitlari.KATEGORIYA}:*")
        return kategoriya
    
    async def asosiy_kategoriyalar_olish(
        self,
        faol_faqat: bool = True
    ) -> List[AsosiyKategoriya]:
        """Barcha asosiy kategoriyalarni oladi."""
        # Keshdan tekshirish
        kesh_kaliti = f"{KeshKalitlari.KATEGORIYA}:asosiy:hammasi"
        keshlangan = await redis_kesh.olish(kesh_kaliti)
        if keshlangan:
            return keshlangan
        
        sorov = select(AsosiyKategoriya).options(
            selectinload(AsosiyKategoriya.kichik_kategoriyalar).selectinload(
                KichikKategoriya.bolimlar
            )
        ).order_by(AsosiyKategoriya.tartib)
        
        if faol_faqat:
            sorov = sorov.where(AsosiyKategoriya.faol == True)
        
        natija = await self.db.execute(sorov)
        kategoriyalar = natija.scalars().all()
        
        return kategoriyalar
    
    async def asosiy_kategoriya_olish(
        self,
        id: UUID
    ) -> Optional[AsosiyKategoriya]:
        """Asosiy kategoriyani kichik kategoriyalar bilan oladi."""
        sorov = select(AsosiyKategoriya).where(
            AsosiyKategoriya.id == id
        ).options(
            selectinload(AsosiyKategoriya.kichik_kategoriyalar).selectinload(
                KichikKategoriya.bolimlar
            )
        )
        natija = await self.db.execute(sorov)
        return natija.scalar_one_or_none()
    
    async def asosiy_kategoriya_slug_bilan(
        self,
        slug: str
    ) -> Optional[AsosiyKategoriya]:
        """Slug bo'yicha asosiy kategoriya oladi."""
        sorov = select(AsosiyKategoriya).where(
            AsosiyKategoriya.slug == slug.lower()
        ).options(
            selectinload(AsosiyKategoriya.kichik_kategoriyalar)
        )
        natija = await self.db.execute(sorov)
        return natija.scalar_one_or_none()
    
    # ============== Kichik Kategoriya ==============
    
    async def kichik_kategoriya_yaratish(
        self,
        malumot: KichikKategoriyaYaratish
    ) -> KichikKategoriya:
        """Kichik kategoriya yaratadi."""
        kategoriya = await self._kichik.yaratish(**malumot.model_dump())
        await redis_kesh.shablon_ochirish(f"{KeshKalitlari.KATEGORIYA}:*")
        return kategoriya
    
    async def kichik_kategoriyalar_olish(
        self,
        asosiy_kategoriya_id: UUID
    ) -> List[KichikKategoriya]:
        """Asosiy kategoriya bo'yicha kichik kategoriyalarni oladi."""
        sorov = select(KichikKategoriya).where(
            and_(
                KichikKategoriya.asosiy_kategoriya_id == asosiy_kategoriya_id,
                KichikKategoriya.faol == True
            )
        ).options(
            selectinload(KichikKategoriya.bolimlar)
        ).order_by(KichikKategoriya.tartib)
        
        natija = await self.db.execute(sorov)
        return natija.scalars().all()
    
    async def kichik_kategoriya_olish(
        self,
        id: UUID
    ) -> Optional[KichikKategoriya]:
        """Kichik kategoriyani bo'limlar bilan oladi."""
        sorov = select(KichikKategoriya).where(
            KichikKategoriya.id == id
        ).options(
            selectinload(KichikKategoriya.bolimlar),
            selectinload(KichikKategoriya.asosiy_kategoriya)
        )
        natija = await self.db.execute(sorov)
        return natija.scalar_one_or_none()
    
    # ============== Bo'lim ==============
    
    async def bolim_yaratish(self, malumot: BolimYaratish) -> Bolim:
        """Bo'lim yaratadi."""
        bolim = await self._bolim.yaratish(**malumot.model_dump())
        await redis_kesh.shablon_ochirish(f"{KeshKalitlari.KATEGORIYA}:*")
        
        # Kichik kategoriya holatlar sonini yangilash kerak bo'lsa
        return bolim
    
    async def bolimlar_olish(
        self,
        kichik_kategoriya_id: UUID
    ) -> List[Bolim]:
        """Kichik kategoriya bo'yicha bo'limlarni oladi."""
        sorov = select(Bolim).where(
            and_(
                Bolim.kichik_kategoriya_id == kichik_kategoriya_id,
                Bolim.faol == True
            )
        ).order_by(Bolim.tartib)
        
        natija = await self.db.execute(sorov)
        return natija.scalars().all()
    
    async def bolim_olish(self, id: UUID) -> Optional[Bolim]:
        """Bo'limni oladi."""
        sorov = select(Bolim).where(Bolim.id == id).options(
            selectinload(Bolim.kichik_kategoriya).selectinload(
                KichikKategoriya.asosiy_kategoriya
            )
        )
        natija = await self.db.execute(sorov)
        return natija.scalar_one_or_none()
    
    async def bolim_slug_bilan(
        self,
        kichik_kategoriya_id: UUID,
        slug: str
    ) -> Optional[Bolim]:
        """Slug bo'yicha bo'lim oladi."""
        sorov = select(Bolim).where(
            and_(
                Bolim.kichik_kategoriya_id == kichik_kategoriya_id,
                Bolim.slug == slug.lower()
            )
        )
        natija = await self.db.execute(sorov)
        return natija.scalar_one_or_none()
    
    # ============== Statistika ==============
    
    async def holatlar_sonini_yangilash(self, bolim_id: UUID) -> None:
        """Bo'limdagi holatlar sonini yangilaydi."""
        from modellar.holat import Holat, QiyinlikDarajasi
        
        # Jami holatlar
        jami_sorov = select(func.count(Holat.id)).where(
            and_(
                Holat.bolim_id == bolim_id,
                Holat.faol == True,
                Holat.chop_etilgan == True
            )
        )
        jami = await self.db.execute(jami_sorov)
        jami_soni = jami.scalar()
        
        # Qiyinlik bo'yicha
        oson_sorov = select(func.count(Holat.id)).where(
            and_(
                Holat.bolim_id == bolim_id,
                Holat.faol == True,
                Holat.chop_etilgan == True,
                Holat.qiyinlik == QiyinlikDarajasi.OSON
            )
        )
        oson = await self.db.execute(oson_sorov)
        
        ortacha_sorov = select(func.count(Holat.id)).where(
            and_(
                Holat.bolim_id == bolim_id,
                Holat.faol == True,
                Holat.chop_etilgan == True,
                Holat.qiyinlik == QiyinlikDarajasi.ORTACHA
            )
        )
        ortacha = await self.db.execute(ortacha_sorov)
        
        qiyin_sorov = select(func.count(Holat.id)).where(
            and_(
                Holat.bolim_id == bolim_id,
                Holat.faol == True,
                Holat.chop_etilgan == True,
                Holat.qiyinlik == QiyinlikDarajasi.QIYIN
            )
        )
        qiyin = await self.db.execute(qiyin_sorov)
        
        # Bo'limni yangilash
        bolim = await self.bolim_olish(bolim_id)
        if bolim:
            bolim.holatlar_soni = jami_soni
            bolim.oson_holatlar = oson.scalar()
            bolim.ortacha_holatlar = ortacha.scalar()
            bolim.qiyin_holatlar = qiyin.scalar()
            await self.db.flush()
    
    async def toliq_statistika(self) -> dict:
        """Barcha kategoriyalar statistikasi."""
        asosiy_soni = await self._asosiy.soni()
        kichik_soni = await self._kichik.soni()
        bolim_soni = await self._bolim.soni()
        
        return {
            "asosiy_kategoriyalar": asosiy_soni,
            "kichik_kategoriyalar": kichik_soni,
            "bolimlar": bolim_soni
        }

    async def asosiy_kategoriya_soni(self) -> int:
        """Aktiv asosiy kategoriyalar sonini qaytaradi."""
        sorov = select(func.count(AsosiyKategoriya.id)).where(AsosiyKategoriya.faol == True)
        natija = await self.db.execute(sorov)
        return natija.scalar()

    async def eng_kop_holatli_kategoriyalar(self, limit: int = 6) -> List[AsosiyKategoriya]:
        """Eng ko'p holatli asosiy kategoriyalarni qaytaradi."""
        from modellar.holat import Holat

        sorov = select(
            AsosiyKategoriya,
            func.count(Holat.id).label('holatlar_soni')
        ).join(
            KichikKategoriya, AsosiyKategoriya.id == KichikKategoriya.asosiy_kategoriya_id
        ).join(
            Bolim, KichikKategoriya.id == Bolim.kichik_kategoriya_id
        ).join(
            Holat, Bolim.id == Holat.bolim_id
        ).where(
            AsosiyKategoriya.faol == True
        ).group_by(
            AsosiyKategoriya.id
        ).order_by(
            func.count(Holat.id).desc()
        ).limit(limit)

        natija = await self.db.execute(sorov)
        return [row.AsosiyKategoriya for row in natija]
    
    # ============== Yangilash va O'chirish ==============
    
    async def asosiy_kategoriya_yangilash(
        self,
        id: UUID,
        malumot
    ) -> Optional[AsosiyKategoriya]:
        """Asosiy kategoriyani yangilaydi."""
        kategoriya = await self.asosiy_kategoriya_olish(id)
        if not kategoriya:
            return None
        
        # Yangilash
        yangilash_dict = malumot.model_dump(exclude_unset=True) if hasattr(malumot, 'model_dump') else malumot
        for kalit, qiymat in yangilash_dict.items():
            if hasattr(kategoriya, kalit) and qiymat is not None:
                setattr(kategoriya, kalit, qiymat)
        
        await self.db.flush()
        await redis_kesh.shablon_ochirish(f"{KeshKalitlari.KATEGORIYA}:*")
        return kategoriya
    
    async def asosiy_kategoriya_ochirish(self, id: UUID) -> bool:
        """Asosiy kategoriyani o'chiradi."""
        kategoriya = await self.asosiy_kategoriya_olish(id)
        if not kategoriya:
            return False
        
        await self.db.delete(kategoriya)
        await self.db.flush()
        await redis_kesh.shablon_ochirish(f"{KeshKalitlari.KATEGORIYA}:*")
        return True
    
    async def kichik_kategoriya_yangilash(
        self,
        id: UUID,
        malumot: dict
    ) -> Optional[KichikKategoriya]:
        """Kichik kategoriyani yangilaydi."""
        kategoriya = await self.kichik_kategoriya_olish(id)
        if not kategoriya:
            return None
        
        for kalit, qiymat in malumot.items():
            if hasattr(kategoriya, kalit) and qiymat is not None:
                setattr(kategoriya, kalit, qiymat)
        
        await self.db.flush()
        await redis_kesh.shablon_ochirish(f"{KeshKalitlari.KATEGORIYA}:*")
        return kategoriya
    
    async def kichik_kategoriya_ochirish(self, id: UUID) -> bool:
        """Kichik kategoriyani o'chiradi."""
        kategoriya = await self.kichik_kategoriya_olish(id)
        if not kategoriya:
            return False
        
        await self.db.delete(kategoriya)
        await self.db.flush()
        await redis_kesh.shablon_ochirish(f"{KeshKalitlari.KATEGORIYA}:*")
        return True
    
    async def bolim_yangilash(
        self,
        id: UUID,
        malumot: dict
    ) -> Optional[Bolim]:
        """Bo'limni yangilaydi."""
        bolim = await self.bolim_olish(id)
        if not bolim:
            return None
        
        for kalit, qiymat in malumot.items():
            if hasattr(bolim, kalit) and qiymat is not None:
                setattr(bolim, kalit, qiymat)
        
        await self.db.flush()
        await redis_kesh.shablon_ochirish(f"{KeshKalitlari.KATEGORIYA}:*")
        return bolim
    
    async def bolim_ochirish(self, id: UUID) -> bool:
        """Bo'limni o'chiradi."""
        bolim = await self.bolim_olish(id)
        if not bolim:
            return False
        
        await self.db.delete(bolim)
        await self.db.flush()
        await redis_kesh.shablon_ochirish(f"{KeshKalitlari.KATEGORIYA}:*")
        return True
