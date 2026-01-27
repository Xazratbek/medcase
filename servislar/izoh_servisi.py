# MedCase Pro Platform - Izoh Servisi
# Forum/Izohlar boshqaruvi

from typing import Optional, List, Tuple
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, delete
from sqlalchemy.orm import selectinload

from modellar.izoh import HolatIzohi, IzohYoqtirishi
from modellar.foydalanuvchi import Foydalanuvchi, FoydalanuvchiProfili
from sxemalar.izoh import IzohYaratish, IzohYangilash


class IzohServisi:
    """Izohlar boshqaruvi servisi."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def yaratish(
        self,
        foydalanuvchi_id: UUID,
        malumot: IzohYaratish
    ) -> HolatIzohi:
        """Yangi izoh yaratadi."""
        izoh = HolatIzohi(
            holat_id=malumot.holat_id,
            foydalanuvchi_id=foydalanuvchi_id,
            ota_izoh_id=malumot.ota_izoh_id,
            matn=malumot.matn
        )
        self.db.add(izoh)
        
        # Agar javob bo'lsa, ota izohning javoblar sonini oshirish
        if malumot.ota_izoh_id:
            ota_izoh = await self.db.get(HolatIzohi, malumot.ota_izoh_id)
            if ota_izoh:
                ota_izoh.javoblar_soni += 1
        
        await self.db.flush()
        await self.db.refresh(izoh)
        return izoh
    
    async def olish(self, izoh_id: UUID) -> Optional[HolatIzohi]:
        """Izohni oladi."""
        sorov = select(HolatIzohi).where(
            and_(HolatIzohi.id == izoh_id, HolatIzohi.faol == True)
        ).options(
            selectinload(HolatIzohi.foydalanuvchi).selectinload(Foydalanuvchi.profil),
            selectinload(HolatIzohi.javoblar)
        )
        natija = await self.db.execute(sorov)
        return natija.scalar_one_or_none()
    
    async def yangilash(
        self,
        izoh_id: UUID,
        foydalanuvchi_id: UUID,
        malumot: IzohYangilash
    ) -> Optional[HolatIzohi]:
        """Izohni yangilaydi."""
        izoh = await self.db.get(HolatIzohi, izoh_id)
        if not izoh or izoh.foydalanuvchi_id != foydalanuvchi_id:
            return None
        
        izoh.matn = malumot.matn
        izoh.tahrirlangan = True
        await self.db.flush()
        return izoh
    
    async def ochirish(
        self,
        izoh_id: UUID,
        foydalanuvchi_id: UUID,
        admin: bool = False
    ) -> bool:
        """Izohni o'chiradi."""
        izoh = await self.db.get(HolatIzohi, izoh_id)
        if not izoh:
            return False
        
        # Faqat o'z izohini yoki admin o'chira oladi
        if not admin and izoh.foydalanuvchi_id != foydalanuvchi_id:
            return False
        
        # Agar ota izoh bo'lsa, javoblar sonini kamaytirish
        if izoh.ota_izoh_id:
            ota_izoh = await self.db.get(HolatIzohi, izoh.ota_izoh_id)
            if ota_izoh:
                ota_izoh.javoblar_soni = max(0, ota_izoh.javoblar_soni - 1)
        
        izoh.faol = False
        await self.db.flush()
        return True
    
    async def holat_izohlari(
        self,
        holat_id: UUID,
        foydalanuvchi_id: Optional[UUID] = None,
        sahifa: int = 1,
        hajm: int = 20
    ) -> Tuple[List[HolatIzohi], int]:
        """Holat izohlarini oladi (faqat asosiy izohlar, javoblar ichida)."""
        # Faqat ota izohsiz (asosiy) izohlarni olish
        sorov = select(HolatIzohi).where(
            and_(
                HolatIzohi.holat_id == holat_id,
                HolatIzohi.ota_izoh_id == None,
                HolatIzohi.faol == True,
                HolatIzohi.moderatsiya_holati == "tasdiqlangan"
            )
        ).options(
            selectinload(HolatIzohi.foydalanuvchi).selectinload(Foydalanuvchi.profil),
            selectinload(HolatIzohi.javoblar).selectinload(HolatIzohi.foydalanuvchi).selectinload(Foydalanuvchi.profil)
        ).order_by(HolatIzohi.yaratilgan_vaqt.desc())
        
        hisob_sorov = select(func.count(HolatIzohi.id)).where(
            and_(
                HolatIzohi.holat_id == holat_id,
                HolatIzohi.ota_izoh_id == None,
                HolatIzohi.faol == True,
                HolatIzohi.moderatsiya_holati == "tasdiqlangan"
            )
        )
        
        offset = (sahifa - 1) * hajm
        sorov = sorov.offset(offset).limit(hajm)
        
        natija = await self.db.execute(sorov)
        jami = await self.db.execute(hisob_sorov)
        izohlar = natija.scalars().all()
        
        # Foydalanuvchi yoqtirishlarini tekshirish
        if foydalanuvchi_id:
            izoh_idlari = [i.id for i in izohlar]
            for izoh in izohlar:
                izoh_idlari.extend([j.id for j in izoh.javoblar])
            
            if izoh_idlari:
                yoq_sorov = select(IzohYoqtirishi.izoh_id).where(
                    and_(
                        IzohYoqtirishi.foydalanuvchi_id == foydalanuvchi_id,
                        IzohYoqtirishi.izoh_id.in_(izoh_idlari)
                    )
                )
                yoq_natija = await self.db.execute(yoq_sorov)
                yoqtirilgan_idlar = set(yoq_natija.scalars().all())
                
                # Yoqtirilgan atributini qo'shish
                for izoh in izohlar:
                    izoh._yoqtirilgan = izoh.id in yoqtirilgan_idlar
                    for javob in izoh.javoblar:
                        javob._yoqtirilgan = javob.id in yoqtirilgan_idlar
        
        return izohlar, jami.scalar()
    
    async def yoqtirish(
        self,
        izoh_id: UUID,
        foydalanuvchi_id: UUID
    ) -> Tuple[bool, int]:
        """Izohni yoqtirish/yoqtirmaydigan qilish."""
        # Mavjud yoqtirishni tekshirish
        sorov = select(IzohYoqtirishi).where(
            and_(
                IzohYoqtirishi.izoh_id == izoh_id,
                IzohYoqtirishi.foydalanuvchi_id == foydalanuvchi_id
            )
        )
        natija = await self.db.execute(sorov)
        mavjud = natija.scalar_one_or_none()
        
        izoh = await self.db.get(HolatIzohi, izoh_id)
        if not izoh:
            return False, 0
        
        if mavjud:
            # Yoqtirishni olib tashlash
            await self.db.delete(mavjud)
            izoh.yoqtirishlar_soni = max(0, izoh.yoqtirishlar_soni - 1)
            yoqtirilgan = False
        else:
            # Yoqtirish qo'shish
            yangi_yoqtirish = IzohYoqtirishi(
                izoh_id=izoh_id,
                foydalanuvchi_id=foydalanuvchi_id
            )
            self.db.add(yangi_yoqtirish)
            izoh.yoqtirishlar_soni += 1
            yoqtirilgan = True
        
        await self.db.flush()
        return yoqtirilgan, izoh.yoqtirishlar_soni
    
    async def foydalanuvchi_izohlari(
        self,
        foydalanuvchi_id: UUID,
        sahifa: int = 1,
        hajm: int = 20
    ) -> Tuple[List[HolatIzohi], int]:
        """Foydalanuvchi izohlarini oladi."""
        sorov = select(HolatIzohi).where(
            and_(
                HolatIzohi.foydalanuvchi_id == foydalanuvchi_id,
                HolatIzohi.faol == True
            )
        ).order_by(HolatIzohi.yaratilgan_vaqt.desc())
        
        hisob_sorov = select(func.count(HolatIzohi.id)).where(
            and_(
                HolatIzohi.foydalanuvchi_id == foydalanuvchi_id,
                HolatIzohi.faol == True
            )
        )
        
        offset = (sahifa - 1) * hajm
        sorov = sorov.offset(offset).limit(hajm)
        
        natija = await self.db.execute(sorov)
        jami = await self.db.execute(hisob_sorov)
        
        return natija.scalars().all(), jami.scalar()
