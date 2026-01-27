# MedCase Pro Platform - Rivojlanish Servisi
# Foydalanuvchi rivojlanishi va statistika

from typing import Optional, List, Tuple
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, update
from sqlalchemy.orm import selectinload
from datetime import datetime, date, timedelta

from modellar.rivojlanish import (
    HolatUrinishi, OqishSessiyasi,
    KunlikStatistika, FoydalanuvchiRivojlanishi,
    BolimRivojlanishi
)
from modellar.holat import Holat, QiyinlikDarajasi
from sxemalar.rivojlanish import UrinishYaratish


class RivojlanishServisi:
    """Foydalanuvchi rivojlanishi servisi."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def urinish_yaratish(
        self,
        foydalanuvchi_id: UUID,
        malumot: UrinishYaratish
    ) -> HolatUrinishi:
        """Yangi urinish yaratadi va statistikani yangilaydi."""
        # Holatni olish
        holat = await self.db.get(Holat, malumot.holat_id)
        if not holat:
            raise ValueError("Holat topilmadi")
        
        # To'g'ri javobni tekshirish
        togri = malumot.tanlangan_javob.upper() == holat.togri_javob
        
        # Ball hisoblash
        olingan_ball = holat.ball if togri else 0
        
        # Urinish yaratish
        hozir = datetime.utcnow()
        urinish = HolatUrinishi(
            foydalanuvchi_id=foydalanuvchi_id,
            holat_id=malumot.holat_id,
            sessiya_id=malumot.sessiya_id,
            tanlangan_javob=malumot.tanlangan_javob.upper(),
            togri=togri,
            sarflangan_vaqt=malumot.sarflangan_vaqt,
            boshlangan_vaqt=hozir - timedelta(seconds=malumot.sarflangan_vaqt),
            tugallangan_vaqt=hozir,
            olingan_ball=olingan_ball
        )
        self.db.add(urinish)
        
        # Statistikalarni yangilash
        await self._rivojlanish_yangilash(
            foydalanuvchi_id, togri, olingan_ball,
            malumot.sarflangan_vaqt, holat.qiyinlik
        )
        await self._kunlik_statistika_yangilash(
            foydalanuvchi_id, togri, olingan_ball,
            malumot.sarflangan_vaqt, holat.qiyinlik
        )
        await self._bolim_rivojlanishi_yangilash(
            foydalanuvchi_id, holat.bolim_id, togri,
            malumot.sarflangan_vaqt
        )
        
        # Sessiyani yangilash
        if malumot.sessiya_id:
            await self._sessiya_yangilash(
                malumot.sessiya_id, togri, olingan_ball
            )
        
        await self.db.flush()
        await self.db.refresh(urinish)
        
        # Nishonlarni tekshirish va berish
        yangi_nishon_nomlari = []
        try:
            from servislar.gamifikatsiya_servisi import GamifikatsiyaServisi
            gamifikatsiya_servis = GamifikatsiyaServisi(self.db)
            yangi_nishonlar = await gamifikatsiya_servis.nishon_tekshirish_va_berish(
                foydalanuvchi_id
            )
            if yangi_nishonlar:
                yangi_nishon_nomlari = [n.nom for n in yangi_nishonlar]
        except Exception:
            pass  # Nishon xatosi asosiy funksiyaga ta'sir qilmasligi kerak
        
        # UrinishJavob schemasi uchun qo'shimcha ma'lumot qaytarish
        # Model atributini o'zgartirib bo'lmaydi, shuning uchun schemada default [] ishlatiladi
        # Agar kerak bo'lsa, marshrut darajasida qo'shimcha ma'lumot qo'shish mumkin
        
        return urinish
    
    async def _rivojlanish_yangilash(
        self,
        foydalanuvchi_id: UUID,
        togri: bool,
        ball: int,
        vaqt: int,
        qiyinlik: QiyinlikDarajasi
    ) -> None:
        """Umumiy rivojlanishni yangilaydi."""
        sorov = select(FoydalanuvchiRivojlanishi).where(
            FoydalanuvchiRivojlanishi.foydalanuvchi_id == foydalanuvchi_id
        )
        natija = await self.db.execute(sorov)
        rivojlanish = natija.scalar_one_or_none()
        
        if not rivojlanish:
            rivojlanish = FoydalanuvchiRivojlanishi(
                foydalanuvchi_id=foydalanuvchi_id,
                jami_urinishlar=0,
                togri_javoblar=0,
                notogri_javoblar=0,
                aniqlik_foizi=0.0,
                jami_vaqt=0,
                ortacha_vaqt=0.0,
                joriy_streak=0,
                eng_uzun_streak=0,
                daraja=1,
                jami_ball=0,
                oson_yechilgan=0,
                oson_togri=0,
                ortacha_yechilgan=0,
                ortacha_togri=0,
                qiyin_yechilgan=0,
                qiyin_togri=0
            )
            self.db.add(rivojlanish)
            await self.db.flush()
        
        rivojlanish.jami_urinishlar = (rivojlanish.jami_urinishlar or 0) + 1
        rivojlanish.jami_vaqt = (rivojlanish.jami_vaqt or 0) + vaqt
        rivojlanish.jami_ball = (rivojlanish.jami_ball or 0) + ball
        
        if togri:
            rivojlanish.togri_javoblar = (rivojlanish.togri_javoblar or 0) + 1
        else:
            rivojlanish.notogri_javoblar = (rivojlanish.notogri_javoblar or 0) + 1
        
        # Qiyinlik bo'yicha
        if qiyinlik == QiyinlikDarajasi.OSON:
            rivojlanish.oson_yechilgan = (rivojlanish.oson_yechilgan or 0) + 1
            if togri:
                rivojlanish.oson_togri = (rivojlanish.oson_togri or 0) + 1
        elif qiyinlik == QiyinlikDarajasi.ORTACHA:
            rivojlanish.ortacha_yechilgan = (rivojlanish.ortacha_yechilgan or 0) + 1
            if togri:
                rivojlanish.ortacha_togri = (rivojlanish.ortacha_togri or 0) + 1
        else:
            rivojlanish.qiyin_yechilgan = (rivojlanish.qiyin_yechilgan or 0) + 1
            if togri:
                rivojlanish.qiyin_togri = (rivojlanish.qiyin_togri or 0) + 1
        
        # Aniqlik va o'rtacha hisoblash
        jami_urinishlar = rivojlanish.jami_urinishlar or 0
        togri_javoblar = rivojlanish.togri_javoblar or 0
        jami_vaqt = rivojlanish.jami_vaqt or 0
        
        if jami_urinishlar > 0:
            rivojlanish.aniqlik_foizi = (togri_javoblar / jami_urinishlar) * 100
            rivojlanish.ortacha_vaqt = jami_vaqt / jami_urinishlar
        
        # Streak yangilash
        bugun = date.today()
        joriy_streak = rivojlanish.joriy_streak or 0
        eng_uzun_streak = rivojlanish.eng_uzun_streak or 0
        
        if rivojlanish.oxirgi_faollik:
            kunlar_farqi = (bugun - rivojlanish.oxirgi_faollik).days
            if kunlar_farqi == 1:
                joriy_streak += 1
            elif kunlar_farqi > 1:
                joriy_streak = 1
        else:
            joriy_streak = 1
        
        rivojlanish.joriy_streak = joriy_streak
        if joriy_streak > eng_uzun_streak:
            rivojlanish.eng_uzun_streak = joriy_streak
        
        rivojlanish.oxirgi_faollik = bugun
        
        # Daraja hisoblash
        rivojlanish.daraja = self._daraja_hisoblash(rivojlanish.jami_ball)
    
    def _daraja_hisoblash(self, ball: int) -> int:
        """Ball asosida darajani hisoblaydi."""
        darajalar = [
            (0, 1), (100, 2), (300, 3), (600, 4), (1000, 5),
            (1500, 6), (2200, 7), (3000, 8), (4000, 9), (5000, 10),
            (6500, 11), (8000, 12), (10000, 13), (12500, 14), (15000, 15)
        ]
        daraja = 1
        for kerakli_ball, dar in darajalar:
            if ball >= kerakli_ball:
                daraja = dar
        return daraja
    
    async def _kunlik_statistika_yangilash(
        self,
        foydalanuvchi_id: UUID,
        togri: bool,
        ball: int,
        vaqt: int,
        qiyinlik: QiyinlikDarajasi
    ) -> None:
        """Kunlik statistikani yangilaydi."""
        bugun = date.today()
        
        # FOR UPDATE bilan qulflash - race condition oldini olish
        sorov = select(KunlikStatistika).where(
            and_(
                KunlikStatistika.foydalanuvchi_id == foydalanuvchi_id,
                KunlikStatistika.sana == bugun
            )
        ).with_for_update(skip_locked=True)
        
        natija = await self.db.execute(sorov)
        statistika = natija.scalar_one_or_none()
        
        if not statistika:
            # Mavjud emas - oddiy so'rov bilan qayta tekshirish
            sorov_tekshir = select(KunlikStatistika).where(
                and_(
                    KunlikStatistika.foydalanuvchi_id == foydalanuvchi_id,
                    KunlikStatistika.sana == bugun
                )
            )
            natija_tekshir = await self.db.execute(sorov_tekshir)
            statistika = natija_tekshir.scalar_one_or_none()
            
            if not statistika:
                # Haqiqatan ham mavjud emas - yangi yaratish
                statistika = KunlikStatistika(
                    foydalanuvchi_id=foydalanuvchi_id,
                    sana=bugun,
                    yechilgan_holatlar=0,
                    togri_javoblar=0,
                    notogri_javoblar=0,
                    jami_vaqt=0,
                    sessiyalar_soni=0,
                    olingan_ball=0,
                    oson_yechilgan=0,
                    ortacha_yechilgan=0,
                    qiyin_yechilgan=0
                )
                self.db.add(statistika)
                await self.db.flush()
        
        statistika.yechilgan_holatlar = (statistika.yechilgan_holatlar or 0) + 1
        statistika.jami_vaqt = (statistika.jami_vaqt or 0) + vaqt
        statistika.olingan_ball = (statistika.olingan_ball or 0) + ball
        
        if togri:
            statistika.togri_javoblar = (statistika.togri_javoblar or 0) + 1
        else:
            statistika.notogri_javoblar = (statistika.notogri_javoblar or 0) + 1
        
        if qiyinlik == QiyinlikDarajasi.OSON:
            statistika.oson_yechilgan = (statistika.oson_yechilgan or 0) + 1
        elif qiyinlik == QiyinlikDarajasi.ORTACHA:
            statistika.ortacha_yechilgan = (statistika.ortacha_yechilgan or 0) + 1
        else:
            statistika.qiyin_yechilgan = (statistika.qiyin_yechilgan or 0) + 1
    
    async def _bolim_rivojlanishi_yangilash(
        self,
        foydalanuvchi_id: UUID,
        bolim_id: UUID,
        togri: bool,
        vaqt: int
    ) -> None:
        """Bo'lim rivojlanishini yangilaydi."""
        sorov = select(BolimRivojlanishi).where(
            and_(
                BolimRivojlanishi.foydalanuvchi_id == foydalanuvchi_id,
                BolimRivojlanishi.bolim_id == bolim_id
            )
        )
        natija = await self.db.execute(sorov)
        bolim_riv = natija.scalar_one_or_none()
        
        if not bolim_riv:
            bolim_riv = BolimRivojlanishi(
                foydalanuvchi_id=foydalanuvchi_id,
                bolim_id=bolim_id,
                jami_holatlar=0,
                yechilgan_holatlar=0,
                togri_javoblar=0,
                aniqlik_foizi=0.0,
                jami_vaqt=0
            )
            self.db.add(bolim_riv)
            await self.db.flush()
        
        bolim_riv.yechilgan_holatlar = (bolim_riv.yechilgan_holatlar or 0) + 1
        bolim_riv.jami_vaqt = (bolim_riv.jami_vaqt or 0) + vaqt
        if togri:
            bolim_riv.togri_javoblar = (bolim_riv.togri_javoblar or 0) + 1
        
        if bolim_riv.yechilgan_holatlar > 0:
            bolim_riv.aniqlik_foizi = (
                bolim_riv.togri_javoblar / bolim_riv.yechilgan_holatlar
            ) * 100
    
    async def _sessiya_yangilash(
        self,
        sessiya_id: UUID,
        togri: bool,
        ball: int
    ) -> None:
        """O'qish sessiyasini yangilaydi."""
        sessiya = await self.db.get(OqishSessiyasi, sessiya_id)
        if sessiya:
            sessiya.yechilgan_holatlar = (sessiya.yechilgan_holatlar or 0) + 1
            sessiya.olingan_ball = (sessiya.olingan_ball or 0) + ball
            if togri:
                sessiya.togri_javoblar = (sessiya.togri_javoblar or 0) + 1
    
    async def rivojlanish_olish(
        self,
        foydalanuvchi_id: UUID
    ) -> Optional[FoydalanuvchiRivojlanishi]:
        """Foydalanuvchi rivojlanishini oladi."""
        sorov = select(FoydalanuvchiRivojlanishi).where(
            FoydalanuvchiRivojlanishi.foydalanuvchi_id == foydalanuvchi_id
        )
        natija = await self.db.execute(sorov)
        return natija.scalar_one_or_none()
    
    async def urinishlar_olish(
        self,
        foydalanuvchi_id: UUID,
        sahifa: int = 1,
        hajm: int = 20
    ) -> Tuple[List[HolatUrinishi], int]:
        """Foydalanuvchi urinishlarini oladi."""
        sorov = select(HolatUrinishi).where(
            HolatUrinishi.foydalanuvchi_id == foydalanuvchi_id
        ).order_by(
            HolatUrinishi.yaratilgan_vaqt.desc()
        )
        
        hisob = select(func.count(HolatUrinishi.id)).where(
            HolatUrinishi.foydalanuvchi_id == foydalanuvchi_id
        )
        
        offset = (sahifa - 1) * hajm
        sorov = sorov.offset(offset).limit(hajm)
        
        natija = await self.db.execute(sorov)
        jami = await self.db.execute(hisob)
        
        return natija.scalars().all(), jami.scalar()
    
    async def sessiya_boshlash(
        self,
        foydalanuvchi_id: UUID,
        qurilma_turi: str = None
    ) -> OqishSessiyasi:
        """Yangi o'qish sessiyasini boshlaydi."""
        sessiya = OqishSessiyasi(
            foydalanuvchi_id=foydalanuvchi_id,
            qurilma_turi=qurilma_turi
        )
        self.db.add(sessiya)
        await self.db.flush()
        return sessiya
    
    async def sessiya_tugatish(self, sessiya_id: UUID) -> OqishSessiyasi:
        """O'qish sessiyasini tugatadi."""
        sessiya = await self.db.get(OqishSessiyasi, sessiya_id)
        if sessiya:
            sessiya.tugallangan_vaqt = datetime.utcnow()
            sessiya.faol = False
            sessiya.davomiylik = int(
                (sessiya.tugallangan_vaqt - sessiya.boshlangan_vaqt).total_seconds()
            )
            await self.db.flush()
        return sessiya
