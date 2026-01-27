# MedCase Pro Platform - Imtihon Servisi
# Timer rejimi va imtihon simulyatsiyasi

from typing import Optional, List, Tuple
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload
from datetime import datetime
import random

from modellar.imtihon import (
    ImtihonShabloni, Imtihon, ImtihonJavobi,
    ImtihonTuri, ImtihonHolati
)
from modellar.holat import Holat, QiyinlikDarajasi
from sxemalar.imtihon import ImtihonBoshlash, ImtihonSavolJavob


class ImtihonServisi:
    """Imtihon simulyatsiyasi servisi."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    # ============== Shablon operatsiyalari ==============
    
    async def shablon_yaratish(self, malumot: dict) -> ImtihonShabloni:
        """Imtihon shabloni yaratish."""
        shablon = ImtihonShabloni(**malumot)
        self.db.add(shablon)
        await self.db.flush()
        await self.db.refresh(shablon)
        return shablon
    
    async def shablonlar_royxati(
        self,
        sahifa: int = 1,
        hajm: int = 20
    ) -> Tuple[List[ImtihonShabloni], int]:
        """Shablonlar ro'yxati."""
        sorov = select(ImtihonShabloni).where(
            ImtihonShabloni.faol == True
        ).order_by(ImtihonShabloni.yaratilgan_vaqt.desc())
        
        hisob_sorov = select(func.count(ImtihonShabloni.id)).where(
            ImtihonShabloni.faol == True
        )
        
        offset = (sahifa - 1) * hajm
        sorov = sorov.offset(offset).limit(hajm)
        
        natija = await self.db.execute(sorov)
        jami = await self.db.execute(hisob_sorov)
        
        return natija.scalars().all(), jami.scalar()
    
    async def shablon_olish(self, shablon_id: UUID) -> Optional[ImtihonShabloni]:
        """Shablonni olish."""
        return await self.db.get(ImtihonShabloni, shablon_id)
    
    # ============== Imtihon operatsiyalari ==============
    
    async def boshlash(
        self,
        foydalanuvchi_id: UUID,
        malumot: ImtihonBoshlash
    ) -> Imtihon:
        """Yangi imtihon boshlash."""
        # Shablon bo'lsa, undan ma'lumotlarni olish
        if malumot.shablon_id:
            shablon = await self.shablon_olish(malumot.shablon_id)
            if shablon:
                nom = shablon.nom
                turi = shablon.turi
                umumiy_vaqt = shablon.umumiy_vaqt
                savol_vaqti = shablon.savol_vaqti
                savollar_soni = shablon.savollar_soni
                aralashtirish = shablon.aralashtirish
                orqaga_qaytish = shablon.orqaga_qaytish
                natijani_korsatish = shablon.natijani_korsatish
                otish_balli = shablon.otish_balli
                kategoriya_idlari = shablon.kategoriya_idlari
                bolim_idlari = shablon.bolim_idlari
                oson_foiz = shablon.oson_foiz
                ortacha_foiz = shablon.ortacha_foiz
                qiyin_foiz = shablon.qiyin_foiz
            else:
                raise ValueError("Shablon topilmadi")
        else:
            nom = malumot.nom or f"Imtihon {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            turi = malumot.turi
            umumiy_vaqt = malumot.umumiy_vaqt
            savol_vaqti = malumot.savol_vaqti
            savollar_soni = malumot.savollar_soni
            aralashtirish = malumot.aralashtirish
            orqaga_qaytish = malumot.orqaga_qaytish
            natijani_korsatish = False  # Default: imtihon oxirida ko'rsatish
            otish_balli = 60
            kategoriya_idlari = malumot.kategoriya_idlari
            bolim_idlari = malumot.bolim_idlari
            oson_foiz = 30
            ortacha_foiz = 50
            qiyin_foiz = 20
        
        # Savollarni tanlash
        savollar = await self._savollar_tanlash(
            savollar_soni, kategoriya_idlari, bolim_idlari,
            oson_foiz, ortacha_foiz, qiyin_foiz, aralashtirish
        )
        
        if len(savollar) < 5:
            raise ValueError("Yetarli savollar topilmadi")
        
        # Imtihon yaratish
        imtihon = Imtihon(
            foydalanuvchi_id=foydalanuvchi_id,
            shablon_id=malumot.shablon_id,
            nom=nom,
            turi=turi,
            holat=ImtihonHolati.JARAYONDA,
            umumiy_vaqt=umumiy_vaqt,
            savol_vaqti=savol_vaqti,
            qolgan_vaqt=umumiy_vaqt if turi == ImtihonTuri.VAQTLI else None,
            boshlangan_vaqt=datetime.utcnow(),
            savollar=[h.id for h in savollar],
            jami_savollar=len(savollar),
            aralashtirish=aralashtirish,
            orqaga_qaytish=orqaga_qaytish,
            natijani_korsatish=natijani_korsatish,
            otish_balli=otish_balli
        )
        self.db.add(imtihon)
        await self.db.flush()
        
        # Javoblar yaratish
        for indeks, holat in enumerate(savollar):
            javob = ImtihonJavobi(
                imtihon_id=imtihon.id,
                holat_id=holat.id,
                savol_indeksi=indeks,
                togri_javob=holat.togri_javob
            )
            self.db.add(javob)
        
        await self.db.flush()
        await self.db.refresh(imtihon)
        return imtihon
    
    async def _savollar_tanlash(
        self,
        soni: int,
        kategoriya_idlari: Optional[List[UUID]],
        bolim_idlari: Optional[List[UUID]],
        oson_foiz: int,
        ortacha_foiz: int,
        qiyin_foiz: int,
        aralashtirish: bool
    ) -> List[Holat]:
        """Savollarni qiyinlik bo'yicha tanlash."""
        filtrlar = [
            Holat.faol == True,
            Holat.chop_etilgan == True
        ]
        
        if bolim_idlari:
            filtrlar.append(Holat.bolim_id.in_(bolim_idlari))
        
        # Har bir qiyinlik uchun kerakli son
        oson_soni = round(soni * oson_foiz / 100)
        ortacha_soni = round(soni * ortacha_foiz / 100)
        qiyin_soni = soni - oson_soni - ortacha_soni
        
        savollar = []
        
        # Oson savollar
        if oson_soni > 0:
            oson_sorov = select(Holat).where(
                and_(*filtrlar, Holat.qiyinlik == QiyinlikDarajasi.OSON)
            ).order_by(func.random()).limit(oson_soni)
            natija = await self.db.execute(oson_sorov)
            savollar.extend(natija.scalars().all())
        
        # O'rtacha savollar
        if ortacha_soni > 0:
            ortacha_sorov = select(Holat).where(
                and_(*filtrlar, Holat.qiyinlik == QiyinlikDarajasi.ORTACHA)
            ).order_by(func.random()).limit(ortacha_soni)
            natija = await self.db.execute(ortacha_sorov)
            savollar.extend(natija.scalars().all())
        
        # Qiyin savollar
        if qiyin_soni > 0:
            qiyin_sorov = select(Holat).where(
                and_(*filtrlar, Holat.qiyinlik == QiyinlikDarajasi.QIYIN)
            ).order_by(func.random()).limit(qiyin_soni)
            natija = await self.db.execute(qiyin_sorov)
            savollar.extend(natija.scalars().all())
        
        # Agar yetarli bo'lmasa, boshqa qiyinliklardan to'ldirish
        if len(savollar) < soni:
            mavjud_idlar = [s.id for s in savollar]
            qoshimcha_sorov = select(Holat).where(
                and_(*filtrlar, Holat.id.notin_(mavjud_idlar) if mavjud_idlar else True)
            ).order_by(func.random()).limit(soni - len(savollar))
            natija = await self.db.execute(qoshimcha_sorov)
            savollar.extend(natija.scalars().all())
        
        # Aralashtirish
        if aralashtirish:
            random.shuffle(savollar)
        
        return savollar
    
    async def olish(
        self,
        imtihon_id: UUID,
        foydalanuvchi_id: UUID
    ) -> Optional[Imtihon]:
        """Imtihonni olish."""
        sorov = select(Imtihon).where(
            and_(
                Imtihon.id == imtihon_id,
                Imtihon.foydalanuvchi_id == foydalanuvchi_id
            )
        ).options(selectinload(Imtihon.javoblar))
        
        natija = await self.db.execute(sorov)
        return natija.scalar_one_or_none()
    
    async def joriy_savol(
        self,
        imtihon_id: UUID,
        foydalanuvchi_id: UUID
    ) -> Optional[dict]:
        """Joriy savolni olish."""
        imtihon = await self.olish(imtihon_id, foydalanuvchi_id)
        if not imtihon or imtihon.holat != ImtihonHolati.JARAYONDA:
            return None
        
        if imtihon.joriy_savol_indeksi >= imtihon.jami_savollar:
            return None
        
        # Savolni olish
        holat_id = imtihon.savollar[imtihon.joriy_savol_indeksi]
        holat = await self.db.get(Holat, holat_id)
        
        if not holat:
            return None
        
        # Variantlarni olish
        from sqlalchemy.orm import selectinload
        sorov = select(Holat).where(Holat.id == holat_id).options(
            selectinload(Holat.variantlar),
            selectinload(Holat.media)
        )
        natija = await self.db.execute(sorov)
        holat = natija.scalar_one_or_none()
        
        # Javob ma'lumotlarini olish
        javob_sorov = select(ImtihonJavobi).where(
            and_(
                ImtihonJavobi.imtihon_id == imtihon_id,
                ImtihonJavobi.savol_indeksi == imtihon.joriy_savol_indeksi
            )
        )
        javob_natija = await self.db.execute(javob_sorov)
        javob = javob_natija.scalar_one_or_none()
        
        # Qolgan vaqtni hisoblash
        qolgan_vaqt = None
        if imtihon.turi == ImtihonTuri.VAQTLI:
            sarflangan = int((datetime.utcnow() - imtihon.boshlangan_vaqt).total_seconds())
            qolgan_vaqt = max(0, imtihon.umumiy_vaqt - sarflangan)
        elif imtihon.turi == ImtihonTuri.IMTIHON:
            if javob and javob.savol_boshlangan:
                sarflangan = int((datetime.utcnow() - javob.savol_boshlangan).total_seconds())
                qolgan_vaqt = max(0, imtihon.savol_vaqti - sarflangan)
            else:
                qolgan_vaqt = imtihon.savol_vaqti
        
        # Savol boshlanish vaqtini belgilash
        if javob and not javob.savol_boshlangan:
            javob.savol_boshlangan = datetime.utcnow()
            await self.db.flush()
        
        variantlar = [
            {"belgi": v.belgi, "matn": v.matn}
            for v in sorted(holat.variantlar, key=lambda x: x.belgi)
        ]
        
        return {
            "savol_indeksi": imtihon.joriy_savol_indeksi,
            "holat_id": holat.id,
            "sarlavha": holat.sarlavha,
            "klinik_stsenariy": holat.klinik_stsenariy,
            "savol": holat.savol,
            "variantlar": variantlar,
            "qiyinlik": holat.qiyinlik.value if holat.qiyinlik else None,
            "media": [{"url": m.url, "turi": m.turi.value} for m in holat.media] if holat.media else [],
            "qolgan_vaqt": qolgan_vaqt,
            "belgilangan": javob.belgilangan if javob else False,
            "javob_berilgan": javob.tanlangan_javob is not None if javob else False,
            "tanlangan_javob": javob.tanlangan_javob if javob else None,
            "jami_savollar": imtihon.jami_savollar,
            "javob_berilgan_soni": imtihon.javob_berilgan
        }
    
    async def javob_berish(
        self,
        imtihon_id: UUID,
        foydalanuvchi_id: UUID,
        malumot: ImtihonSavolJavob
    ) -> dict:
        """Savolga javob berish."""
        imtihon = await self.olish(imtihon_id, foydalanuvchi_id)
        if not imtihon or imtihon.holat != ImtihonHolati.JARAYONDA:
            raise ValueError("Imtihon topilmadi yoki yakunlangan")
        
        # Javobni olish
        javob_sorov = select(ImtihonJavobi).where(
            and_(
                ImtihonJavobi.imtihon_id == imtihon_id,
                ImtihonJavobi.savol_indeksi == malumot.savol_indeksi
            )
        )
        javob_natija = await self.db.execute(javob_sorov)
        javob = javob_natija.scalar_one_or_none()
        
        if not javob:
            raise ValueError("Savol topilmadi")
        
        # Javob yangilash
        if malumot.otkazish:
            javob.otkazilgan = True
            imtihon.otkazilgan_savollar += 1
        elif malumot.tanlangan_javob:
            javob.tanlangan_javob = malumot.tanlangan_javob.upper()
            javob.togri = javob.tanlangan_javob == javob.togri_javob
            javob.javob_berilgan_vaqt = datetime.utcnow()
            
            if javob.savol_boshlangan:
                javob.sarflangan_vaqt = int(
                    (javob.javob_berilgan_vaqt - javob.savol_boshlangan).total_seconds()
                )
            
            imtihon.javob_berilgan += 1
            if javob.togri:
                imtihon.togri_javoblar += 1
            else:
                imtihon.notogri_javoblar += 1
        
        javob.belgilangan = malumot.belgilangan
        
        await self.db.flush()
        
        # Natijani qaytarish
        natija = {
            "savol_indeksi": malumot.savol_indeksi,
            "javob_berilgan": javob.tanlangan_javob is not None,
            "otkazilgan": javob.otkazilgan
        }
        
        # Agar natijani ko'rsatish kerak bo'lsa
        if imtihon.natijani_korsatish and javob.tanlangan_javob:
            natija["togri"] = javob.togri
            natija["togri_javob"] = javob.togri_javob
        
        return natija
    
    async def keyingi_savol(
        self,
        imtihon_id: UUID,
        foydalanuvchi_id: UUID
    ) -> Optional[dict]:
        """Keyingi savolga o'tish."""
        imtihon = await self.olish(imtihon_id, foydalanuvchi_id)
        if not imtihon or imtihon.holat != ImtihonHolati.JARAYONDA:
            return None
        
        if imtihon.joriy_savol_indeksi < imtihon.jami_savollar - 1:
            imtihon.joriy_savol_indeksi += 1
            await self.db.flush()
        
        return await self.joriy_savol(imtihon_id, foydalanuvchi_id)
    
    async def oldingi_savol(
        self,
        imtihon_id: UUID,
        foydalanuvchi_id: UUID
    ) -> Optional[dict]:
        """Oldingi savolga qaytish."""
        imtihon = await self.olish(imtihon_id, foydalanuvchi_id)
        if not imtihon or imtihon.holat != ImtihonHolati.JARAYONDA:
            return None
        
        if not imtihon.orqaga_qaytish:
            return None
        
        if imtihon.joriy_savol_indeksi > 0:
            imtihon.joriy_savol_indeksi -= 1
            await self.db.flush()
        
        return await self.joriy_savol(imtihon_id, foydalanuvchi_id)
    
    async def savolga_otish(
        self,
        imtihon_id: UUID,
        foydalanuvchi_id: UUID,
        savol_indeksi: int
    ) -> Optional[dict]:
        """Ma'lum savolga o'tish."""
        imtihon = await self.olish(imtihon_id, foydalanuvchi_id)
        if not imtihon or imtihon.holat != ImtihonHolati.JARAYONDA:
            return None
        
        if not imtihon.orqaga_qaytish and savol_indeksi < imtihon.joriy_savol_indeksi:
            return None
        
        if 0 <= savol_indeksi < imtihon.jami_savollar:
            imtihon.joriy_savol_indeksi = savol_indeksi
            await self.db.flush()
        
        return await self.joriy_savol(imtihon_id, foydalanuvchi_id)
    
    async def yakunlash(
        self,
        imtihon_id: UUID,
        foydalanuvchi_id: UUID
    ) -> Imtihon:
        """Imtihonni yakunlash."""
        imtihon = await self.olish(imtihon_id, foydalanuvchi_id)
        if not imtihon:
            raise ValueError("Imtihon topilmadi")
        
        if imtihon.holat == ImtihonHolati.TUGALLANGAN:
            return imtihon
        
        imtihon.holat = ImtihonHolati.TUGALLANGAN
        imtihon.tugallangan_vaqt = datetime.utcnow()
        
        # Ball hisoblash
        if imtihon.javob_berilgan > 0:
            imtihon.ball_foizi = round(
                (imtihon.togri_javoblar / imtihon.jami_savollar) * 100
            )
        else:
            imtihon.ball_foizi = 0
        
        imtihon.otgan = imtihon.ball_foizi >= imtihon.otish_balli
        
        # Shablon statistikasini yangilash
        if imtihon.shablon_id:
            shablon = await self.shablon_olish(imtihon.shablon_id)
            if shablon:
                shablon.otkazilgan_soni += 1
                # O'rtacha ball yangilash (oddiy formula)
                jami = shablon.ortacha_ball * (shablon.otkazilgan_soni - 1)
                shablon.ortacha_ball = round((jami + imtihon.ball_foizi) / shablon.otkazilgan_soni)
        
        await self.db.flush()
        await self.db.refresh(imtihon)
        return imtihon
    
    async def foydalanuvchi_imtihonlari(
        self,
        foydalanuvchi_id: UUID,
        sahifa: int = 1,
        hajm: int = 20
    ) -> Tuple[List[Imtihon], int]:
        """Foydalanuvchi imtihonlari."""
        sorov = select(Imtihon).where(
            Imtihon.foydalanuvchi_id == foydalanuvchi_id
        ).order_by(Imtihon.yaratilgan_vaqt.desc())
        
        hisob_sorov = select(func.count(Imtihon.id)).where(
            Imtihon.foydalanuvchi_id == foydalanuvchi_id
        )
        
        offset = (sahifa - 1) * hajm
        sorov = sorov.offset(offset).limit(hajm)
        
        natija = await self.db.execute(sorov)
        jami = await self.db.execute(hisob_sorov)
        
        return natija.scalars().all(), jami.scalar()
    
    async def statistika(self, foydalanuvchi_id: UUID) -> dict:
        """Imtihon statistikasi."""
        sorov = select(
            func.count(Imtihon.id),
            func.count(Imtihon.id).filter(Imtihon.holat == ImtihonHolati.TUGALLANGAN),
            func.count(Imtihon.id).filter(Imtihon.otgan == True),
            func.count(Imtihon.id).filter(Imtihon.otgan == False),
            func.avg(Imtihon.ball_foizi),
            func.max(Imtihon.ball_foizi),
            func.min(Imtihon.ball_foizi).filter(Imtihon.ball_foizi > 0)
        ).where(Imtihon.foydalanuvchi_id == foydalanuvchi_id)
        
        natija = await self.db.execute(sorov)
        row = natija.one()
        
        return {
            "jami_imtihonlar": row[0] or 0,
            "tugallangan_imtihonlar": row[1] or 0,
            "otgan_imtihonlar": row[2] or 0,
            "otmagan_imtihonlar": row[3] or 0,
            "ortacha_ball": round(row[4] or 0, 1),
            "eng_yuqori_ball": row[5] or 0,
            "eng_past_ball": row[6] or 0
        }
