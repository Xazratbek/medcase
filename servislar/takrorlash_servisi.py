# MedCase Pro Platform - Takrorlash Servisi (Spaced Repetition)
# SM-2 algoritmi bilan takrorlash tizimi

from typing import Optional, List, Tuple
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload
from datetime import datetime, date, timedelta

from modellar.takrorlash import TakrorlashKartasi, TakrorlashTarixi, TakrorlashSessiyasi
from modellar.holat import Holat
from modellar.kategoriya import Bolim, KichikKategoriya
from sxemalar.takrorlash import TakrorlashBaholash


class TakrorlashServisi:
    """Spaced Repetition (SM-2) servisi."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def karta_olish_yoki_yaratish(
        self,
        foydalanuvchi_id: UUID,
        holat_id: UUID
    ) -> TakrorlashKartasi:
        """Kartani olish yoki yangi yaratish."""
        sorov = select(TakrorlashKartasi).where(
            and_(
                TakrorlashKartasi.foydalanuvchi_id == foydalanuvchi_id,
                TakrorlashKartasi.holat_id == holat_id
            )
        )
        natija = await self.db.execute(sorov)
        karta = natija.scalar_one_or_none()
        
        if not karta:
            karta = TakrorlashKartasi(
                foydalanuvchi_id=foydalanuvchi_id,
                holat_id=holat_id,
                keyingi_takrorlash=date.today()
            )
            self.db.add(karta)
            await self.db.flush()
            await self.db.refresh(karta)
        
        return karta
    
    async def baholash(
        self,
        foydalanuvchi_id: UUID,
        holat_id: UUID,
        malumot: TakrorlashBaholash
    ) -> TakrorlashKartasi:
        """SM-2 algoritmi bilan baholash."""
        karta = await self.karta_olish_yoki_yaratish(foydalanuvchi_id, holat_id)
        
        # Tarix uchun eski qiymatlar
        ef_oldin = karta.easiness_factor
        interval_oldin = karta.interval
        
        # SM-2 hisoblash
        karta.sm2_hisoblash(malumot.sifat)
        
        # Tarix yaratish
        tarix = TakrorlashTarixi(
            karta_id=karta.id,
            sifat=malumot.sifat,
            togri=malumot.sifat >= 3,
            sarflangan_vaqt=malumot.sarflangan_vaqt,
            ef_oldin=ef_oldin,
            ef_keyin=karta.easiness_factor,
            interval_oldin=interval_oldin,
            interval_keyin=karta.interval
        )
        self.db.add(tarix)
        
        await self.db.flush()
        await self.db.refresh(karta)
        return karta
    
    async def bugungi_kartalar(
        self,
        foydalanuvchi_id: UUID,
        limit: int = 50
    ) -> List[TakrorlashKartasi]:
        """Bugun takrorlash kerak bo'lgan kartalar."""
        bugun = date.today()
        sorov = select(TakrorlashKartasi).where(
            and_(
                TakrorlashKartasi.foydalanuvchi_id == foydalanuvchi_id,
                TakrorlashKartasi.keyingi_takrorlash <= bugun,
                TakrorlashKartasi.oqilgan == False,
                TakrorlashKartasi.faol == True
            )
        ).options(
            selectinload(TakrorlashKartasi.holat).selectinload(Holat.bolim)
        ).order_by(
            TakrorlashKartasi.keyingi_takrorlash.asc()
        ).limit(limit)
        
        natija = await self.db.execute(sorov)
        kartalar = natija.scalars().all()
        
        # Holat ma'lumotlarini qo'shish
        for karta in kartalar:
            if karta.holat:
                karta.holat_sarlavhasi = karta.holat.sarlavha
                karta.holat_qiyinligi = karta.holat.qiyinlik.value if karta.holat.qiyinlik else None
                if karta.holat.bolim:
                    karta.kategoriya_nomi = karta.holat.bolim.nomi
        
        return kartalar
    
    async def barcha_kartalar(
        self,
        foydalanuvchi_id: UUID,
        sahifa: int = 1,
        hajm: int = 20,
        faqat_bugungi: bool = False
    ) -> Tuple[List[TakrorlashKartasi], int]:
        """Foydalanuvchi barcha kartalari."""
        filtrlar = [
            TakrorlashKartasi.foydalanuvchi_id == foydalanuvchi_id,
            TakrorlashKartasi.faol == True
        ]
        
        if faqat_bugungi:
            filtrlar.append(TakrorlashKartasi.keyingi_takrorlash <= date.today())
            filtrlar.append(TakrorlashKartasi.oqilgan == False)
        
        sorov = select(TakrorlashKartasi).where(
            and_(*filtrlar)
        ).options(
            selectinload(TakrorlashKartasi.holat)
        ).order_by(TakrorlashKartasi.keyingi_takrorlash.asc())
        
        hisob_sorov = select(func.count(TakrorlashKartasi.id)).where(and_(*filtrlar))
        
        offset = (sahifa - 1) * hajm
        sorov = sorov.offset(offset).limit(hajm)
        
        natija = await self.db.execute(sorov)
        jami = await self.db.execute(hisob_sorov)
        
        return natija.scalars().all(), jami.scalar()
    
    async def statistika(self, foydalanuvchi_id: UUID) -> dict:
        """Takrorlash statistikasi."""
        bugun = date.today()
        ertaga = bugun + timedelta(days=1)
        hafta = bugun + timedelta(days=7)
        
        # Jami kartalar
        jami_sorov = select(func.count(TakrorlashKartasi.id)).where(
            and_(
                TakrorlashKartasi.foydalanuvchi_id == foydalanuvchi_id,
                TakrorlashKartasi.faol == True
            )
        )
        
        # Bugun takrorlash kerak
        bugun_sorov = select(func.count(TakrorlashKartasi.id)).where(
            and_(
                TakrorlashKartasi.foydalanuvchi_id == foydalanuvchi_id,
                TakrorlashKartasi.keyingi_takrorlash <= bugun,
                TakrorlashKartasi.oqilgan == False,
                TakrorlashKartasi.faol == True
            )
        )
        
        # Ertaga takrorlash kerak
        ertaga_sorov = select(func.count(TakrorlashKartasi.id)).where(
            and_(
                TakrorlashKartasi.foydalanuvchi_id == foydalanuvchi_id,
                TakrorlashKartasi.keyingi_takrorlash == ertaga,
                TakrorlashKartasi.oqilgan == False,
                TakrorlashKartasi.faol == True
            )
        )
        
        # Hafta ichida
        hafta_sorov = select(func.count(TakrorlashKartasi.id)).where(
            and_(
                TakrorlashKartasi.foydalanuvchi_id == foydalanuvchi_id,
                TakrorlashKartasi.keyingi_takrorlash <= hafta,
                TakrorlashKartasi.oqilgan == False,
                TakrorlashKartasi.faol == True
            )
        )
        
        # O'rtacha EF
        ef_sorov = select(func.avg(TakrorlashKartasi.easiness_factor)).where(
            and_(
                TakrorlashKartasi.foydalanuvchi_id == foydalanuvchi_id,
                TakrorlashKartasi.faol == True
            )
        )
        
        # Jami takrorlashlar va aniqlik
        stat_sorov = select(
            func.sum(TakrorlashKartasi.jami_takrorlashlar),
            func.sum(TakrorlashKartasi.togri_javoblar)
        ).where(
            and_(
                TakrorlashKartasi.foydalanuvchi_id == foydalanuvchi_id,
                TakrorlashKartasi.faol == True
            )
        )
        
        jami = await self.db.execute(jami_sorov)
        bugun_natija = await self.db.execute(bugun_sorov)
        ertaga_natija = await self.db.execute(ertaga_sorov)
        hafta_natija = await self.db.execute(hafta_sorov)
        ef_natija = await self.db.execute(ef_sorov)
        stat_natija = await self.db.execute(stat_sorov)
        
        jami_takrorlashlar, togri_javoblar = stat_natija.one()
        jami_takrorlashlar = jami_takrorlashlar or 0
        togri_javoblar = togri_javoblar or 0
        
        aniqlik = (togri_javoblar / jami_takrorlashlar * 100) if jami_takrorlashlar > 0 else 0
        
        return {
            "jami_kartalar": jami.scalar() or 0,
            "bugun_takrorlash_kerak": bugun_natija.scalar() or 0,
            "ertaga_takrorlash_kerak": ertaga_natija.scalar() or 0,
            "hafta_ichida": hafta_natija.scalar() or 0,
            "ortacha_ef": round(ef_natija.scalar() or 2.5, 2),
            "jami_takrorlashlar": jami_takrorlashlar,
            "umumiy_aniqlik": round(aniqlik, 1),
            "streak_kunlar": 0  # TODO: Streak hisoblash
        }
    
    async def kartani_oqilgan_qilish(
        self,
        foydalanuvchi_id: UUID,
        holat_id: UUID,
        oqilgan: bool = True
    ) -> Optional[TakrorlashKartasi]:
        """Kartani o'qilgan deb belgilash."""
        sorov = select(TakrorlashKartasi).where(
            and_(
                TakrorlashKartasi.foydalanuvchi_id == foydalanuvchi_id,
                TakrorlashKartasi.holat_id == holat_id
            )
        )
        natija = await self.db.execute(sorov)
        karta = natija.scalar_one_or_none()
        
        if karta:
            karta.oqilgan = oqilgan
            await self.db.flush()
        
        return karta
    
    async def holatni_takrorlashga_qoshish(
        self,
        foydalanuvchi_id: UUID,
        holat_id: UUID
    ) -> TakrorlashKartasi:
        """Holatni takrorlash kartasiga qo'shish."""
        return await self.karta_olish_yoki_yaratish(foydalanuvchi_id, holat_id)
    
    async def karta_tarixi(
        self,
        karta_id: UUID,
        limit: int = 20
    ) -> List[TakrorlashTarixi]:
        """Karta tarixini olish."""
        sorov = select(TakrorlashTarixi).where(
            TakrorlashTarixi.karta_id == karta_id
        ).order_by(
            TakrorlashTarixi.yaratilgan_vaqt.desc()
        ).limit(limit)
        
        natija = await self.db.execute(sorov)
        return natija.scalars().all()
