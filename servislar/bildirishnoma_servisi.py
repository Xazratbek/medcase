# MedCase Pro Platform - Bildirishnoma Servisi
# Foydalanuvchi bildirishnomalari boshqaruvi

from typing import Optional, List, Tuple
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, update
from datetime import datetime

from modellar.bildirishnoma import (
    Bildirishnoma, BildirishnomaTuri, BildirishnomaSozlamalari
)


class BildirishnomServisi:
    """Bildirishnomalar boshqaruvi servisi."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def yaratish(
        self,
        foydalanuvchi_id: UUID,
        turi: BildirishnomaTuri,
        sarlavha: str,
        matn: str,
        havola: str = None,
        qoshimcha: dict = None
    ) -> Bildirishnoma:
        """Yangi bildirishnoma yaratadi."""
        bildirishnoma = Bildirishnoma(
            foydalanuvchi_id=foydalanuvchi_id,
            turi=turi,
            sarlavha=sarlavha,
            matn=matn,
            havola=havola,
            qoshimcha_malumot=qoshimcha or {}
        )
        self.db.add(bildirishnoma)
        await self.db.flush()
        return bildirishnoma
    
    async def ommaviy_yaratish(
        self,
        turi: BildirishnomaTuri,
        sarlavha: str,
        matn: str,
        havola: str = None,
        qoshimcha: dict = None
    ):
        """Barcha foydalanuvchilarga bildirishnoma yaratadi."""
        from modellar.foydalanuvchi import Foydalanuvchi
        
        # Barcha foydalanuvchilar IDlarini olish
        sorov = select(Foydalanuvchi.id)
        natija = await self.db.execute(sorov)
        foydalanuvchi_idlar = natija.scalars().all()
        
        # Har bir foydalanuvchi uchun bildirishnoma yaratish
        bildirishnomalar = [
            Bildirishnoma(
                foydalanuvchi_id=foyd_id,
                turi=turi,
                sarlavha=sarlavha,
                matn=matn,
                havola=havola,
                qoshimcha_malumot=qoshimcha or {}
            )
            for foyd_id in foydalanuvchi_idlar
        ]
        
        self.db.add_all(bildirishnomalar)
        await self.db.flush()

    async def royxat_olish(
        self,
        foydalanuvchi_id: UUID,
        oqilmagan_faqat: bool = False,
        sahifa: int = 1,
        hajm: int = 20
    ) -> Tuple[List[Bildirishnoma], int]:
        """Foydalanuvchi bildirishnomalarini oladi."""
        filtrlar = [Bildirishnoma.foydalanuvchi_id == foydalanuvchi_id]
        
        if oqilmagan_faqat:
            filtrlar.append(Bildirishnoma.oqilgan == False)
        
        sorov = select(Bildirishnoma).where(
            and_(*filtrlar)
        ).order_by(Bildirishnoma.yaratilgan_vaqt.desc())
        
        hisob = select(func.count(Bildirishnoma.id)).where(and_(*filtrlar))
        
        offset = (sahifa - 1) * hajm
        sorov = sorov.offset(offset).limit(hajm)
        
        natija = await self.db.execute(sorov)
        jami = await self.db.execute(hisob)
        
        return natija.scalars().all(), jami.scalar()
    
    async def oqilmagan_soni(self, foydalanuvchi_id: UUID) -> int:
        """O'qilmagan bildirishnomalar sonini qaytaradi."""
        sorov = select(func.count(Bildirishnoma.id)).where(
            and_(
                Bildirishnoma.foydalanuvchi_id == foydalanuvchi_id,
                Bildirishnoma.oqilgan == False
            )
        )
        natija = await self.db.execute(sorov)
        return natija.scalar()
    
    async def oqilgan_belgilash(
        self,
        bildirishnoma_id: UUID,
        foydalanuvchi_id: UUID
    ) -> bool:
        """Bildirishnomani o'qilgan deb belgilaydi."""
        sorov = update(Bildirishnoma).where(
            and_(
                Bildirishnoma.id == bildirishnoma_id,
                Bildirishnoma.foydalanuvchi_id == foydalanuvchi_id
            )
        ).values(oqilgan=True, oqilgan_vaqt=datetime.utcnow())
        
        natija = await self.db.execute(sorov)
        await self.db.flush()
        return natija.rowcount > 0
    
    async def hammasini_oqilgan_belgilash(
        self,
        foydalanuvchi_id: UUID
    ) -> int:
        """Barcha bildirishnomalarni o'qilgan deb belgilaydi."""
        sorov = update(Bildirishnoma).where(
            and_(
                Bildirishnoma.foydalanuvchi_id == foydalanuvchi_id,
                Bildirishnoma.oqilgan == False
            )
        ).values(oqilgan=True, oqilgan_vaqt=datetime.utcnow())
        
        natija = await self.db.execute(sorov)
        await self.db.flush()
        return natija.rowcount
    
    # ============== Maxsus bildirishnomalar ==============
    
    async def nishon_bildirish(
        self,
        foydalanuvchi_id: UUID,
        nishon_nomi: str,
        nishon_id: UUID
    ) -> Bildirishnoma:
        """Yangi nishon haqida bildiradi."""
        return await self.yaratish(
            foydalanuvchi_id=foydalanuvchi_id,
            turi=BildirishnomaTuri.NISHON,
            sarlavha="Yangi nishon qo'lga kiritildi! 🏆",
            matn=f"Tabriklaymiz! Siz '{nishon_nomi}' nishonini qo'lga kiritdingiz.",
            havola=f"/nishonlar/{nishon_id}",
            qoshimcha={"nishon_id": str(nishon_id)}
        )
    
    async def daraja_bildirish(
        self,
        foydalanuvchi_id: UUID,
        yangi_daraja: int
    ) -> Bildirishnoma:
        """Yangi daraja haqida bildiradi."""
        return await self.yaratish(
            foydalanuvchi_id=foydalanuvchi_id,
            turi=BildirishnomaTuri.YUTUQ,
            sarlavha=f"Yangi daraja: {yangi_daraja} 🎉",
            matn=f"Ajoyib! Siz {yangi_daraja}-darajaga ko'tarildingiz!",
            havola="/profil",
            qoshimcha={"daraja": yangi_daraja}
        )
    
    async def streak_eslatma(
        self,
        foydalanuvchi_id: UUID,
        joriy_streak: int
    ) -> Bildirishnoma:
        """Streak eslatmasi."""
        return await self.yaratish(
            foydalanuvchi_id=foydalanuvchi_id,
            turi=BildirishnomaTuri.STREAK,
            sarlavha="Streak saqlab qoling! 🔥",
            matn=f"Sizning {joriy_streak} kunlik streak'ingiz bor. Bugun ham mashq qiling!",
            havola="/mashq"
        )
    
    # ============== Sozlamalar ==============
    
    async def sozlamalar_olish(
        self,
        foydalanuvchi_id: UUID
    ) -> Optional[BildirishnomaSozlamalari]:
        """Bildirishnoma sozlamalarini oladi."""
        sorov = select(BildirishnomaSozlamalari).where(
            BildirishnomaSozlamalari.foydalanuvchi_id == foydalanuvchi_id
        )
        natija = await self.db.execute(sorov)
        return natija.scalar_one_or_none()
    
    async def sozlamalar_yangilash(
        self,
        foydalanuvchi_id: UUID,
        **sozlamalar
    ) -> BildirishnomaSozlamalari:
        """Bildirishnoma sozlamalarini yangilaydi."""
        sozlama = await self.sozlamalar_olish(foydalanuvchi_id)
        
        if not sozlama:
            sozlama = BildirishnomaSozlamalari(
                foydalanuvchi_id=foydalanuvchi_id,
                **sozlamalar
            )
            self.db.add(sozlama)
        else:
            for kalit, qiymat in sozlamalar.items():
                if hasattr(sozlama, kalit):
                    setattr(sozlama, kalit, qiymat)
        
        await self.db.flush()
        return sozlama
