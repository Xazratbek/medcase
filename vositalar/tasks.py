# MedCase Pro Platform - background tasks

from celery import shared_task
from typing import List
import json
import asyncio

from pywebpush import webpush, WebPushException

from sozlamalar.sozlamalar import sozlamalar
from sozlamalar.malumotlar_bazasi import malumotlar_bazasi
from modellar.bildirishnoma import PushObuna, BildirishnomaSozlamalari, BildirishnomaTuri
from modellar.foydalanuvchi import Foydalanuvchi
from sqlalchemy import select, and_


@shared_task
def ping() -> str:
    return "pong"


async def _push_obunalarni_olish():
    async with malumotlar_bazasi.sessiya() as db:
        sorov = select(
            PushObuna,
            BildirishnomaSozlamalari
        ).join(
            BildirishnomaSozlamalari,
            PushObuna.foydalanuvchi_id == BildirishnomaSozlamalari.foydalanuvchi_id
        ).join(
            Foydalanuvchi,
            Foydalanuvchi.id == PushObuna.foydalanuvchi_id
        ).where(
            and_(
                Foydalanuvchi.faol == True,
                BildirishnomaSozlamalari.push_yangi_kontent == True
            )
        )
        natija = await db.execute(sorov)
        return natija.all()


async def _obunani_ochirish(endpoint: str):
    async with malumotlar_bazasi.sessiya() as db:
        sorov = select(PushObuna).where(PushObuna.endpoint == endpoint)
        natija = await db.execute(sorov)
        obuna = natija.scalar_one_or_none()
        if obuna:
            await db.delete(obuna)
            await db.flush()


@shared_task
def yangi_holat_push(holat_id: str, sarlavha: str):
    """Yangi holat qo'shilganda push yuborish."""
    if not sozlamalar.vapid_public_key or not sozlamalar.vapid_private_key:
        return

    async def _run():
        rows = await _push_obunalarni_olish()
        for obuna, _ in rows:
            subscription = {
                "endpoint": obuna.endpoint,
                "keys": {
                    "p256dh": obuna.p256dh,
                    "auth": obuna.auth
                }
            }
            payload = {
                "title": "Yangi holat qo'shildi!",
                "body": sarlavha,
                "url": f"/holat/{holat_id}",
                "silent": False
            }
            try:
                webpush(
                    subscription_info=subscription,
                    data=json.dumps(payload),
                    vapid_private_key=sozlamalar.vapid_private_key,
                    vapid_claims={"sub": sozlamalar.vapid_subject}
                )
            except WebPushException as exc:
                status_code = getattr(exc.response, "status_code", None)
                if status_code in (404, 410):
                    await _obunani_ochirish(obuna.endpoint)

    asyncio.run(_run())
