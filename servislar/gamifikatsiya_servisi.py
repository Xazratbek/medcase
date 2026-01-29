# MedCase Pro Platform - Gamifikatsiya Servisi
# Nishonlar, ballar va reytinglar boshqaruvi

from typing import Optional, List, Tuple
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc
from datetime import datetime, date, timedelta

from modellar.gamifikatsiya import (
    Nishon, FoydalanuvchiNishoni, Ball, Reyting,
    NishonTuri, DarajaKonfiguratsiyasi
)
from modellar.rivojlanish import FoydalanuvchiRivojlanishi
from modellar.foydalanuvchi import Foydalanuvchi


class GamifikatsiyaServisi:
    """Gamifikatsiya servisi."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    # ============== Nishonlar ==============
    
    async def nishonlar_olish(self) -> List[Nishon]:
        """Barcha nishonlarni oladi."""
        sorov = select(Nishon).where(Nishon.faol == True).order_by(Nishon.turi)
        natija = await self.db.execute(sorov)
        return natija.scalars().all()
    
    async def foydalanuvchi_nishonlari(
        self,
        foydalanuvchi_id: UUID
    ) -> List[FoydalanuvchiNishoni]:
        """Foydalanuvchi nishonlarini oladi."""
        sorov = select(FoydalanuvchiNishoni).where(
            FoydalanuvchiNishoni.foydalanuvchi_id == foydalanuvchi_id
        ).order_by(FoydalanuvchiNishoni.qolga_kiritilgan_vaqt.desc())
        natija = await self.db.execute(sorov)
        return natija.scalars().all()
    
    async def nishon_tekshirish_va_berish(
        self,
        foydalanuvchi_id: UUID
    ) -> List[Nishon]:
        """Foydalanuvchi yangi nishonlarga ega bo'lishi mumkinligini tekshiradi."""
        yangi_nishonlar = []
        
        # Rivojlanishni olish
        riv_sorov = select(FoydalanuvchiRivojlanishi).where(
            FoydalanuvchiRivojlanishi.foydalanuvchi_id == foydalanuvchi_id
        )
        riv_natija = await self.db.execute(riv_sorov)
        rivojlanish = riv_natija.scalar_one_or_none()
        
        if not rivojlanish:
            return []
        
        # Mavjud nishonlar
        mavjud_sorov = select(FoydalanuvchiNishoni.nishon_id).where(
            FoydalanuvchiNishoni.foydalanuvchi_id == foydalanuvchi_id
        )
        mavjud_natija = await self.db.execute(mavjud_sorov)
        mavjud_idlar = set(mavjud_natija.scalars().all())
        
        # Barcha nishonlarni tekshirish
        nishonlar = await self.nishonlar_olish()
        
        for nishon in nishonlar:
            if nishon.id in mavjud_idlar:
                continue
            
            # Shartlarni tekshirish
            if await self._shartlar_bajarilgan(rivojlanish, nishon):
                # Nishon berish
                foyd_nishon = FoydalanuvchiNishoni(
                    foydalanuvchi_id=foydalanuvchi_id,
                    nishon_id=nishon.id,
                    qolga_kiritilgan_vaqt=datetime.utcnow()
                )
                self.db.add(foyd_nishon)
                
                # Ball berish
                await self.ball_qoshish(
                    foydalanuvchi_id,
                    nishon.ball_qiymati,
                    "nishon",
                    f"Nishon: {nishon.nom}",
                    nishon_id=nishon.id
                )
                
                # Nishon statistikasini yangilash
                nishon.ega_bolganlar_soni += 1
                
                yangi_nishonlar.append(nishon)
        
        await self.db.flush()
        return yangi_nishonlar
    
    async def _shartlar_bajarilgan(
        self,
        rivojlanish: FoydalanuvchiRivojlanishi,
        nishon: Nishon
    ) -> bool:
        """Nishon shartlari bajarilganligini tekshiradi."""
        shartlar = nishon.ochish_shartlari
        shart_turi = shartlar.get("turi")
        qiymat = shartlar.get("qiymat", 0)
        
        if shart_turi == "holatlar_soni":
            return rivojlanish.jami_urinishlar >= qiymat
        elif shart_turi == "togri_javoblar":
            return rivojlanish.togri_javoblar >= qiymat
        elif shart_turi == "streak":
            return rivojlanish.joriy_streak >= qiymat
        elif shart_turi == "aniqlik":
            return rivojlanish.aniqlik_foizi >= qiymat
        elif shart_turi == "daraja":
            return rivojlanish.daraja >= qiymat
        elif shart_turi == "ball":
            return rivojlanish.jami_ball >= qiymat
        elif shart_turi == "vaqt":
            return rivojlanish.jami_vaqt >= qiymat * 3600  # soatda
        
        return False
    
    # ============== Ballar ==============
    
    async def ball_qoshish(
        self,
        foydalanuvchi_id: UUID,
        miqdor: int,
        sabab: str,
        tavsif: str = None,
        holat_id: UUID = None,
        nishon_id: UUID = None
    ) -> Ball:
        """Foydalanuvchiga ball qo'shadi."""
        ball = Ball(
            foydalanuvchi_id=foydalanuvchi_id,
            miqdor=miqdor,
            sabab=sabab,
            tavsif=tavsif,
            holat_id=holat_id,
            nishon_id=nishon_id
        )
        self.db.add(ball)
        
        # Rivojlanishdagi jami ballni yangilash
        riv_sorov = select(FoydalanuvchiRivojlanishi).where(
            FoydalanuvchiRivojlanishi.foydalanuvchi_id == foydalanuvchi_id
        )
        riv_natija = await self.db.execute(riv_sorov)
        rivojlanish = riv_natija.scalar_one_or_none()
        
        if rivojlanish:
            rivojlanish.jami_ball += miqdor
        
        await self.db.flush()
        return ball
    
    async def ball_tarixi(
        self,
        foydalanuvchi_id: UUID,
        sahifa: int = 1,
        hajm: int = 20
    ) -> Tuple[List[Ball], int]:
        """Ball tarixini oladi."""
        sorov = select(Ball).where(
            Ball.foydalanuvchi_id == foydalanuvchi_id
        ).order_by(Ball.yaratilgan_vaqt.desc())
        
        hisob = select(func.count(Ball.id)).where(
            Ball.foydalanuvchi_id == foydalanuvchi_id
        )
        
        offset = (sahifa - 1) * hajm
        sorov = sorov.offset(offset).limit(hajm)
        
        natija = await self.db.execute(sorov)
        jami = await self.db.execute(hisob)
        
        return natija.scalars().all(), jami.scalar()
    
    # ============== Reyting ==============
    
    async def reyting_yangilash(self, turi: str = "global") -> None:
        """Reytingni yangilaydi."""
        # Eski reytingni o'chirish
        from sqlalchemy import delete
        del_sorov = delete(Reyting).where(Reyting.turi == turi)
        await self.db.execute(del_sorov)
        
        # Yangi reyting yaratish
        sorov = select(
            FoydalanuvchiRivojlanishi.foydalanuvchi_id,
            FoydalanuvchiRivojlanishi.jami_ball,
            FoydalanuvchiRivojlanishi.jami_urinishlar,
            FoydalanuvchiRivojlanishi.aniqlik_foizi
        ).order_by(
            FoydalanuvchiRivojlanishi.jami_ball.desc()
        ).limit(1000)
        
        natija = await self.db.execute(sorov)
        foydalanuvchilar = natija.all()
        
        for orni, (foyd_id, ball, holatlar, aniqlik) in enumerate(foydalanuvchilar, 1):
            reyting = Reyting(
                foydalanuvchi_id=foyd_id,
                turi=turi,
                orni=orni,
                ball=ball,
                holatlar_soni=holatlar,
                aniqlik=aniqlik
            )
            self.db.add(reyting)
        
        await self.db.flush()

        # Real-time reyting yangilanishi
        try:
            from servislar.websocket_servisi import reyting_yangilash_yuborish
            royxat, _ = await self.reyting_olish(turi=turi, sahifa=1, hajm=50)
            await reyting_yangilash_yuborish(royxat, royxat[:3])
        except Exception:
            pass
    
    async def reyting_olish(
        self,
        turi: str = "global",
        sahifa: int = 1,
        hajm: int = 50
    ) -> Tuple[List[dict], int]:
        """Reytingni oladi."""
        sorov = select(
            Reyting,
            Foydalanuvchi.foydalanuvchi_nomi,
            Foydalanuvchi.ism,
            Foydalanuvchi.familiya
        ).join(
            Foydalanuvchi,
            Reyting.foydalanuvchi_id == Foydalanuvchi.id
        ).where(
            Reyting.turi == turi
        ).order_by(Reyting.orni)
        
        hisob = select(func.count(Reyting.id)).where(Reyting.turi == turi)
        
        offset = (sahifa - 1) * hajm
        sorov = sorov.offset(offset).limit(hajm)
        
        natija = await self.db.execute(sorov)
        jami = await self.db.execute(hisob)
        
        royxat = []
        for reyting, nom, ism, familiya in natija.all():
            royxat.append({
                "orni": reyting.orni,
                "foydalanuvchi_id": reyting.foydalanuvchi_id,
                "foydalanuvchi_nomi": nom,
                "toliq_ism": f"{ism} {familiya}",
                "ball": reyting.ball,
                "holatlar_soni": reyting.holatlar_soni,
                "aniqlik": reyting.aniqlik
            })
        
        return royxat, jami.scalar()
    
    async def foydalanuvchi_orni(
        self,
        foydalanuvchi_id: UUID,
        turi: str = "global"
    ) -> Optional[int]:
        """Foydalanuvchining reyting o'rnini oladi."""
        sorov = select(Reyting.orni).where(
            and_(
                Reyting.foydalanuvchi_id == foydalanuvchi_id,
                Reyting.turi == turi
            )
        )
        natija = await self.db.execute(sorov)
        return natija.scalar_one_or_none()
    
    # ============== Daraja ==============
    
    async def daraja_konfiguratsiyasi(self) -> List[DarajaKonfiguratsiyasi]:
        """Daraja konfiguratsiyasini oladi."""
        sorov = select(DarajaKonfiguratsiyasi).order_by(
            DarajaKonfiguratsiyasi.daraja
        )
        natija = await self.db.execute(sorov)
        return natija.scalars().all()
