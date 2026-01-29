# MedCase Pro Platform - Push bildirishnoma servisi

from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime, time
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from modellar.bildirishnoma import PushObuna, BildirishnomaSozlamalari, BildirishnomaTuri


class PushServisi:
    """Push obunalarini boshqarish va filtrlar."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def obuna_saqlash(
        self,
        foydalanuvchi_id: UUID,
        endpoint: str,
        p256dh: str,
        auth: str,
        content_encoding: str = "aesgcm",
        user_agent: Optional[str] = None
    ) -> PushObuna:
        """Push obunasini saqlaydi yoki yangilaydi."""
        sorov = select(PushObuna).where(PushObuna.endpoint == endpoint)
        natija = await self.db.execute(sorov)
        obuna = natija.scalar_one_or_none()

        if not obuna:
            obuna = PushObuna(
                foydalanuvchi_id=foydalanuvchi_id,
                endpoint=endpoint,
                p256dh=p256dh,
                auth=auth,
                content_encoding=content_encoding,
                user_agent=user_agent
            )
            self.db.add(obuna)
        else:
            obuna.foydalanuvchi_id = foydalanuvchi_id
            obuna.p256dh = p256dh
            obuna.auth = auth
            obuna.content_encoding = content_encoding
            obuna.user_agent = user_agent

        await self.db.flush()
        return obuna

    async def obunani_ochirish(self, endpoint: str, foydalanuvchi_id: UUID) -> bool:
        """Push obunasini o'chiradi."""
        sorov = select(PushObuna).where(
            and_(
                PushObuna.endpoint == endpoint,
                PushObuna.foydalanuvchi_id == foydalanuvchi_id
            )
        )
        natija = await self.db.execute(sorov)
        obuna = natija.scalar_one_or_none()

        if not obuna:
            return False

        await self.db.delete(obuna)
        await self.db.flush()
        return True

    async def foydalanuvchi_obunalari(self, foydalanuvchi_id: UUID) -> List[PushObuna]:
        """Foydalanuvchining barcha push obunalarini oladi."""
        sorov = select(PushObuna).where(PushObuna.foydalanuvchi_id == foydalanuvchi_id)
        natija = await self.db.execute(sorov)
        return natija.scalars().all()

    async def push_ruxsat_bormi(
        self,
        foydalanuvchi_id: UUID,
        turi: BildirishnomaTuri
    ) -> bool:
        """Foydalanuvchi push sozlamasi ruxsatini tekshiradi."""
        sorov = select(BildirishnomaSozlamalari).where(
            BildirishnomaSozlamalari.foydalanuvchi_id == foydalanuvchi_id
        )
        natija = await self.db.execute(sorov)
        sozlama = natija.scalar_one_or_none()
        if not sozlama:
            return False

        # Sokin rejim tekshirish
        if sozlama.sokin_rejim:
            try:
                now = datetime.now().time()
                boshlanish = time.fromisoformat(sozlama.sokin_boshlanish)
                tugash = time.fromisoformat(sozlama.sokin_tugash)
                if boshlanish < tugash:
                    if boshlanish <= now <= tugash:
                        return False
                else:
                    if now >= boshlanish or now <= tugash:
                        return False
            except Exception:
                pass

        if turi == BildirishnomaTuri.YUTUQ or turi == BildirishnomaTuri.NISHON:
            return sozlama.push_yutuqlar
        if turi == BildirishnomaTuri.STREAK:
            return sozlama.push_streak
        if turi == BildirishnomaTuri.REYTING:
            return sozlama.push_reyting
        if turi == BildirishnomaTuri.ESLATMA:
            return sozlama.push_eslatma
        if turi == BildirishnomaTuri.YANGI_KONTENT:
            return sozlama.push_yangi_kontent

        return False
