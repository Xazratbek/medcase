# MedCase Pro Platform - Holat Servisi
# Klinik holatlar boshqaruvi

from typing import Optional, List, Tuple
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, update
from sqlalchemy.orm import selectinload, joinedload, load_only

from servislar.asosiy_servis import AsosiyServis
from modellar.holat import (
    Holat, HolatVarianti, HolatMedia, HolatTegi,
    HolatTuri, QiyinlikDarajasi, MediaTuri
)
from modellar.rivojlanish import HolatUrinishi
from sxemalar.holat import (
    HolatYaratish, HolatYangilash, HolatQidirish,
    VariantYaratish, MediaYaratish
)
from sozlamalar.redis_kesh import redis_kesh, KeshKalitlari


class HolatServisi:
    """Klinik holatlar boshqaruvi servisi."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self._holat = AsosiyServis(Holat, db)
    
    async def yaratish(self, malumot: HolatYaratish) -> Holat:
        """Yangi holat yaratadi."""
        # Asosiy holat
        holat_malumot = malumot.model_dump(
            exclude={"variantlar", "media", "teg_idlari"}
        )
        holat = Holat(**holat_malumot)
        self.db.add(holat)
        await self.db.flush()
        
        # Variantlar
        for variant_malumot in malumot.variantlar:
            variant = HolatVarianti(
                holat_id=holat.id,
                **variant_malumot.model_dump()
            )
            self.db.add(variant)
        
        # Media
        for media_malumot in malumot.media:
            media = HolatMedia(
                holat_id=holat.id,
                **media_malumot.model_dump()
            )
            self.db.add(media)
        
        # Teglar
        if malumot.teg_idlari:
            for teg_id in malumot.teg_idlari:
                teg = await self.db.get(HolatTegi, teg_id)
                if teg:
                    holat.teglar.append(teg)
        
        await self.db.flush()
        await self.db.refresh(holat)
        
        # Keshni tozalash
        await redis_kesh.shablon_ochirish(f"{KeshKalitlari.HOLAT}:*")
        
        return holat
    
    async def olish(self, id: UUID) -> Optional[Holat]:
        """Holatni to'liq oladi."""
        from modellar.kategoriya import Bolim, KichikKategoriya, AsosiyKategoriya
        sorov = select(Holat).where(Holat.id == id).options(
            selectinload(Holat.variantlar),
            selectinload(Holat.media),
            selectinload(Holat.teglar),
            joinedload(Holat.bolim).joinedload(
                Bolim.kichik_kategoriya
            ).joinedload(
                KichikKategoriya.asosiy_kategoriya
            )
        )
        natija = await self.db.execute(sorov)
        holat = natija.scalar_one_or_none()
        
        if holat and holat.bolim:
            holat.bolim_nomi = holat.bolim.nomi
            if holat.bolim.kichik_kategoriya:
                holat.kichik_kategoriya_nomi = holat.bolim.kichik_kategoriya.nomi
                if holat.bolim.kichik_kategoriya.asosiy_kategoriya:
                    holat.asosiy_kategoriya_nomi = holat.bolim.kichik_kategoriya.asosiy_kategoriya.nomi
        
        return holat
    
    async def yangilash(
        self,
        id: UUID,
        malumot: HolatYangilash
    ) -> Optional[Holat]:
        """Holatni yangilaydi."""
        holat = await self._holat.yangilash(
            id,
            **malumot.model_dump(exclude_unset=True)
        )
        await redis_kesh.shablon_ochirish(f"{KeshKalitlari.HOLAT}:*")
        return holat
    
    async def qidirish(
        self,
        malumot: HolatQidirish,
        foydalanuvchi_id: UUID = None
    ) -> Tuple[List[Holat], int]:
        """Holatlarni qidiradi va filtrlay."""
        from modellar.kategoriya import Bolim, KichikKategoriya, AsosiyKategoriya
        
        # Optimallashtirish: joinedload va load_only ishlatish
        sorov = select(Holat).options(
            selectinload(Holat.variantlar).load_only(
                HolatVarianti.id, HolatVarianti.belgi, 
                HolatVarianti.matn, HolatVarianti.togri,
                HolatVarianti.holat_id, HolatVarianti.tushuntirish
            ),
            selectinload(Holat.media).load_only(
                HolatMedia.id, HolatMedia.holat_id, HolatMedia.turi,
                HolatMedia.url, HolatMedia.nom, HolatMedia.tavsif,
                HolatMedia.tartib, HolatMedia.cloudinary_id,
                HolatMedia.fayl_hajmi, HolatMedia.kenglik,
                HolatMedia.balandlik, HolatMedia.davomiylik
            ),
            selectinload(Holat.teglar).load_only(
                HolatTegi.id, HolatTegi.nom, HolatTegi.slug, HolatTegi.rang
            ),
            joinedload(Holat.bolim).load_only(
                Bolim.id, Bolim.nomi
            ).joinedload(Bolim.kichik_kategoriya).load_only(
                KichikKategoriya.id, KichikKategoriya.nomi
            ).joinedload(KichikKategoriya.asosiy_kategoriya).load_only(
                AsosiyKategoriya.id, AsosiyKategoriya.nomi
            )
        )
        hisob_sorov = select(func.count(Holat.id))
        
        # Filtrlar
        filtrlar = [Holat.faol == True]
        
        if malumot.chop_etilgan is not None:
            filtrlar.append(Holat.chop_etilgan == malumot.chop_etilgan)
        else:
            filtrlar.append(Holat.chop_etilgan == True)
        
        if malumot.bolim_id:
            filtrlar.append(Holat.bolim_id == malumot.bolim_id)
        
        if malumot.turi:
            filtrlar.append(Holat.turi == malumot.turi)
        
        if malumot.qiyinlik:
            filtrlar.append(Holat.qiyinlik == malumot.qiyinlik)
        
        if malumot.qidiruv:
            qidiruv_pattern = f"%{malumot.qidiruv}%"
            filtrlar.append(
                or_(
                    Holat.sarlavha.ilike(qidiruv_pattern),
                    Holat.klinik_stsenariy.ilike(qidiruv_pattern),
                    Holat.savol.ilike(qidiruv_pattern)
                )
            )
        
        # Foydalanuvchi yechgan/yechmagan
        if foydalanuvchi_id and malumot.yechilgan is not None:
            yechilgan_subsorov = select(HolatUrinishi.holat_id).where(
                HolatUrinishi.foydalanuvchi_id == foydalanuvchi_id
            ).distinct()
            
            if malumot.yechilgan:
                filtrlar.append(Holat.id.in_(yechilgan_subsorov))
            else:
                filtrlar.append(Holat.id.notin_(yechilgan_subsorov))
        
        sorov = sorov.where(and_(*filtrlar))
        hisob_sorov = hisob_sorov.where(and_(*filtrlar))
        
        # Saralash
        saralash_maydoni = getattr(Holat, malumot.saralash, Holat.yaratilgan_vaqt)
        if malumot.tartib == "desc":
            sorov = sorov.order_by(saralash_maydoni.desc())
        else:
            sorov = sorov.order_by(saralash_maydoni.asc())
        
        # Sahifalash
        offset = (malumot.sahifa - 1) * malumot.hajm
        sorov = sorov.offset(offset).limit(malumot.hajm)
        
        natija = await self.db.execute(sorov)
        jami = await self.db.execute(hisob_sorov)
        
        holatlar = natija.scalars().all()
        # Kategoriya nomlarini qo'shish
        for holat in holatlar:
            if holat.bolim:
                holat.bolim_nomi = holat.bolim.nomi
                if holat.bolim.kichik_kategoriya:
                    holat.kichik_kategoriya_nomi = holat.bolim.kichik_kategoriya.nomi
                    if holat.bolim.kichik_kategoriya.asosiy_kategoriya:
                        holat.asosiy_kategoriya_nomi = holat.bolim.kichik_kategoriya.asosiy_kategoriya.nomi
        
        return holatlar, jami.scalar()
    
    async def bolim_boyicha(
        self,
        bolim_id: UUID,
        sahifa: int = 1,
        hajm: int = 20
    ) -> Tuple[List[Holat], int]:
        """Bo'lim bo'yicha holatlarni oladi."""
        sorov = select(Holat).where(
            and_(
                Holat.bolim_id == bolim_id,
                Holat.faol == True,
                Holat.chop_etilgan == True
            )
        ).options(
            selectinload(Holat.variantlar),
            selectinload(Holat.media),
            selectinload(Holat.teglar)
        ).order_by(Holat.yaratilgan_vaqt.desc())
        
        hisob_sorov = select(func.count(Holat.id)).where(
            and_(
                Holat.bolim_id == bolim_id,
                Holat.faol == True,
                Holat.chop_etilgan == True
            )
        )
        
        offset = (sahifa - 1) * hajm
        sorov = sorov.offset(offset).limit(hajm)
        
        natija = await self.db.execute(sorov)
        jami = await self.db.execute(hisob_sorov)
        
        return natija.scalars().all(), jami.scalar()
    
    async def tasodifiy_olish(
        self,
        soni: int = 10,
        bolim_id: UUID = None,
        qiyinlik: QiyinlikDarajasi = None,
        istisno_idlar: List[UUID] = None
    ) -> List[Holat]:
        """Tasodifiy holatlar oladi."""
        filtrlar = [
            Holat.faol == True,
            Holat.chop_etilgan == True
        ]
        
        if bolim_id:
            filtrlar.append(Holat.bolim_id == bolim_id)
        
        if qiyinlik:
            filtrlar.append(Holat.qiyinlik == qiyinlik)
        
        if istisno_idlar:
            filtrlar.append(Holat.id.notin_(istisno_idlar))
        
        sorov = select(Holat).where(
            and_(*filtrlar)
        ).options(
            selectinload(Holat.variantlar),
            selectinload(Holat.media),
            selectinload(Holat.teglar)
        ).order_by(func.random()).limit(soni)
        
        natija = await self.db.execute(sorov)
        return natija.scalars().all()
    
    async def statistika_yangilash(
        self,
        holat_id: UUID,
        togri: bool
    ) -> None:
        """Holat statistikasini yangilaydi."""
        holat = await self.db.get(Holat, holat_id)
        if holat:
            holat.urinishlar_soni += 1
            if togri:
                holat.togri_javoblar += 1
            await self.db.flush()
    
    # ============== Teg operatsiyalari ==============
    
    async def teg_yaratish(
        self,
        nom: str,
        slug: str,
        rang: str = "#6B7280"
    ) -> HolatTegi:
        """Yangi teg yaratadi."""
        teg = HolatTegi(nom=nom, slug=slug.lower(), rang=rang)
        self.db.add(teg)
        await self.db.flush()
        return teg
    
    async def teglar_olish(self) -> List[HolatTegi]:
        """Barcha teglarni oladi."""
        sorov = select(HolatTegi).where(
            HolatTegi.faol == True
        ).order_by(HolatTegi.nom)
        natija = await self.db.execute(sorov)
        return natija.scalars().all()
    
    # ============== Media operatsiyalari ==============
    
    async def media_qoshish(
        self,
        holat_id: UUID,
        malumot: MediaYaratish
    ) -> HolatMedia:
        """Holatga media qo'shadi."""
        media = HolatMedia(holat_id=holat_id, **malumot.model_dump())
        self.db.add(media)
        await self.db.flush()
        return media
    
    async def media_ochirish(self, media_id: UUID) -> bool:
        """Mediani o'chiradi."""
        media = await self.db.get(HolatMedia, media_id)
        if media:
            await self.db.delete(media)
            await self.db.flush()
            return True
        return False

    async def soni(self) -> int:
        """Aktiv va chop etilgan holatlar sonini qaytaradi."""
        sorov = select(func.count(Holat.id)).where(
            and_(
                Holat.faol == True,
                Holat.chop_etilgan == True
            )
        )
        natija = await self.db.execute(sorov)
        return natija.scalar()
    
    # ============== Admin operatsiyalari ==============
    
    async def ochirish(self, holat_id: UUID) -> bool:
        """Holatni o'chiradi."""
        holat = await self.db.get(Holat, holat_id)
        if holat:
            await self.db.delete(holat)
            await self.db.flush()
            return True
        return False
