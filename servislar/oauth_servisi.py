# MedCase Pro Platform - OAuth (Google) Servisi
# Google ID token tekshirish va foydalanuvchini ulash/yaratish

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4
import re
import secrets

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from modellar.foydalanuvchi import Foydalanuvchi, OAuthHisob
from modellar.rivojlanish import FoydalanuvchiRivojlanishi
from modellar.foydalanuvchi import FoydalanuvchiProfili
from servislar.autentifikatsiya_servisi import AutentifikatsiyaServisi
from yordamchilar.xavfsizlik import parol_hashlash
from sozlamalar.sozlamalar import sozlamalar


class OAuthServisi:
    """Google OAuth orqali kirish servisi."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def google_token_tekshirish(self, token: str) -> dict:
        """Google ID tokenni tekshiradi va foydalanuvchi ma'lumotlarini qaytaradi."""
        if not sozlamalar.google_client_id:
            raise ValueError("GOOGLE_CLIENT_ID sozlanmagan")

        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(
                "https://oauth2.googleapis.com/tokeninfo",
                params={"id_token": token}
            )

        if resp.status_code != 200:
            raise ValueError("Google token yaroqsiz")

        data = resp.json()
        if data.get("aud") != sozlamalar.google_client_id:
            raise ValueError("Google token aud mos emas")

        return data

    def _foydalanuvchi_nomi_asos(self, email: str) -> str:
        asos = (email or "user").split("@")[0]
        asos = re.sub(r"[^a-zA-Z0-9_]", "_", asos).strip("_").lower()
        if len(asos) < 3:
            asos = f"user_{secrets.token_hex(2)}"
        return asos[:40]

    async def _foydalanuvchi_nomi_unique(self, asos: str) -> str:
        nom = asos
        idx = 1
        while True:
            sorov = select(Foydalanuvchi.id).where(Foydalanuvchi.foydalanuvchi_nomi == nom)
            mavjud = await self.db.execute(sorov)
            if not mavjud.scalar_one_or_none():
                return nom
            nom = f"{asos}_{idx}"
            if len(nom) > 50:
                nom = nom[:50]
            idx += 1

    async def _yangi_foydalanuvchi_yaratish(self, data: dict) -> Foydalanuvchi:
        email = (data.get("email") or "").lower()
        ism = (data.get("given_name") or "").strip() or "Foydalanuvchi"
        familiya = (data.get("family_name") or "").strip() or "Google"
        avatar_url = data.get("picture")

        asos = self._foydalanuvchi_nomi_asos(email)
        foydalanuvchi_nomi = await self._foydalanuvchi_nomi_unique(asos)

        parol = secrets.token_urlsafe(24)
        parol_hash = parol_hashlash(parol)

        foydalanuvchi_id = uuid4()
        foydalanuvchi = Foydalanuvchi(
            id=foydalanuvchi_id,
            email=email,
            foydalanuvchi_nomi=foydalanuvchi_nomi,
            parol_hash=parol_hash,
            ism=ism,
            familiya=familiya,
            email_tasdiqlangan=str(data.get("email_verified", "false")).lower() == "true"
        )

        profil = FoydalanuvchiProfili(
            id=uuid4(),
            foydalanuvchi_id=foydalanuvchi_id,
            avatar_url=avatar_url
        )
        rivojlanish = FoydalanuvchiRivojlanishi(
            id=uuid4(),
            foydalanuvchi_id=foydalanuvchi_id
        )

        self.db.add_all([foydalanuvchi, profil, rivojlanish])
        await self.db.flush()
        return foydalanuvchi

    async def google_kirish(self, token: str, qurilma_malumoti: dict | None = None):
        data = await self.google_token_tekshirish(token)

        sub = data.get("sub")
        if not sub:
            raise ValueError("Google token ma'lumotlari to'liq emas")

        sorov = (
            select(OAuthHisob)
            .options(joinedload(OAuthHisob.foydalanuvchi))
            .where(
                OAuthHisob.provayder == "google",
                OAuthHisob.provayder_foydalanuvchi_id == sub
            )
        )
        natija = await self.db.execute(sorov)
        oauth_hisob = natija.scalar_one_or_none()

        foydalanuvchi: Optional[Foydalanuvchi] = None
        if oauth_hisob:
            foydalanuvchi = oauth_hisob.foydalanuvchi
        else:
            email = (data.get("email") or "").lower()
            if email:
                sorov = select(Foydalanuvchi).where(Foydalanuvchi.email == email)
                natija = await self.db.execute(sorov)
                foydalanuvchi = natija.scalar_one_or_none()

            if not foydalanuvchi:
                foydalanuvchi = await self._yangi_foydalanuvchi_yaratish(data)

            oauth_hisob = OAuthHisob(
                id=uuid4(),
                foydalanuvchi_id=foydalanuvchi.id,
                provayder="google",
                provayder_foydalanuvchi_id=sub
            )
            self.db.add(oauth_hisob)

        if not foydalanuvchi or not foydalanuvchi.faol:
            raise ValueError("Hisob faol emas")

        # OAuth ma'lumotlarini yangilash
        oauth_hisob.kirish_tokeni = token
        exp = data.get("exp")
        if exp:
            try:
                oauth_hisob.token_amal_qilish_vaqti = datetime.fromtimestamp(int(exp), tz=timezone.utc)
            except Exception:
                pass

        await self.db.flush()

        auth_servis = AutentifikatsiyaServisi(self.db)
        return await auth_servis.kirish(foydalanuvchi, qurilma_malumoti=qurilma_malumoti)
