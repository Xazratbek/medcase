# MedCase Platform - Gamifikatsiya Marshrutlari
# Nishonlar, ballar va reyting

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID

from sozlamalar.malumotlar_bazasi import sessiya_olish
from servislar.gamifikatsiya_servisi import GamifikatsiyaServisi
from sxemalar.gamifikatsiya import (
    NishonJavob,
    NishonlarRoyxati,
    FoydalanuvchiNishoniJavob,
    BalllarRoyxati,
    ReytingRoyxati,
    DarajaRivojlanishi
)
from middleware.autentifikatsiya import joriy_foydalanuvchi_olish
from modellar.foydalanuvchi import Foydalanuvchi

router = APIRouter()


@router.get(
    "/nishonlar",
    response_model=NishonlarRoyxati,
    summary="Nishonlar ro'yxati"
)
async def nishonlar_royxati(
    joriy_foydalanuvchi: Foydalanuvchi = Depends(joriy_foydalanuvchi_olish),
    db: AsyncSession = Depends(sessiya_olish)
):
    """
    Barcha nishonlar va foydalanuvchi qo'lga kiritgan nishonlar.
    """
    servis = GamifikatsiyaServisi(db)
    
    barcha = await servis.nishonlar_olish()
    qolga_kiritilgan = await servis.foydalanuvchi_nishonlari(joriy_foydalanuvchi.id)
    
    qolga_kiritilgan_idlar = {n.nishon_id for n in qolga_kiritilgan}
    qolga_kiritilmagan = [n for n in barcha if n.id not in qolga_kiritilgan_idlar]
    
    return NishonlarRoyxati(
        barcha_nishonlar=barcha,
        qolga_kiritilgan=qolga_kiritilgan,
        qolga_kiritilmagan=qolga_kiritilmagan
    )


@router.get(
    "/nishonlar/mening",
    response_model=List[FoydalanuvchiNishoniJavob],
    summary="Mening nishonlarim"
)
async def mening_nishonlarim(
    joriy_foydalanuvchi: Foydalanuvchi = Depends(joriy_foydalanuvchi_olish),
    db: AsyncSession = Depends(sessiya_olish)
):
    """
    Foydalanuvchi qo'lga kiritgan nishonlar.
    """
    servis = GamifikatsiyaServisi(db)
    return await servis.foydalanuvchi_nishonlari(joriy_foydalanuvchi.id)


@router.get(
    "/ballar",
    response_model=BalllarRoyxati,
    summary="Ball tarixi"
)
async def ball_tarixi(
    sahifa: int = Query(1, ge=1),
    hajm: int = Query(20, ge=1, le=100),
    joriy_foydalanuvchi: Foydalanuvchi = Depends(joriy_foydalanuvchi_olish),
    db: AsyncSession = Depends(sessiya_olish)
):
    """
    Foydalanuvchi ball tarixi.
    """
    servis = GamifikatsiyaServisi(db)
    ballar, jami = await servis.ball_tarixi(joriy_foydalanuvchi.id, sahifa, hajm)
    
    jami_ball = sum(b.miqdor for b in ballar)
    
    return BalllarRoyxati(
        ballar=ballar,
        jami_ball=jami_ball,
        sahifa=sahifa,
        hajm=hajm
    )


@router.get(
    "/reyting",
    response_model=ReytingRoyxati,
    summary="Reyting jadvali"
)
async def reyting_jadvali(
    turi: str = Query("global", description="Reyting turi"),
    sahifa: int = Query(1, ge=1),
    hajm: int = Query(50, ge=1, le=100),
    joriy_foydalanuvchi: Foydalanuvchi = Depends(joriy_foydalanuvchi_olish),
    db: AsyncSession = Depends(sessiya_olish)
):
    """
    Reyting jadvalini qaytaradi.
    """
    servis = GamifikatsiyaServisi(db)
    foydalanuvchilar, jami = await servis.reyting_olish(turi, sahifa, hajm)
    joriy_orni = await servis.foydalanuvchi_orni(joriy_foydalanuvchi.id, turi)
    
    return ReytingRoyxati(
        foydalanuvchilar=foydalanuvchilar,
        joriy_foydalanuvchi_orni=joriy_orni,
        jami=jami
    )


@router.get(
    "/daraja",
    response_model=DarajaRivojlanishi,
    summary="Daraja rivojlanishi"
)
async def daraja_rivojlanishi(
    joriy_foydalanuvchi: Foydalanuvchi = Depends(joriy_foydalanuvchi_olish),
    db: AsyncSession = Depends(sessiya_olish)
):
    """
    Joriy daraja va keyingi darajaga rivojlanish.
    """
    from servislar.rivojlanish_servisi import RivojlanishServisi
    
    riv_servis = RivojlanishServisi(db)
    gam_servis = GamifikatsiyaServisi(db)
    
    rivojlanish = await riv_servis.rivojlanish_olish(joriy_foydalanuvchi.id)
    darajalar = await gam_servis.daraja_konfiguratsiyasi()
    
    joriy_ball = rivojlanish.jami_ball if rivojlanish else 0
    joriy_daraja_raqam = rivojlanish.daraja if rivojlanish else 1
    
    joriy_daraja = None
    keyingi_daraja = None
    
    for i, daraja in enumerate(darajalar):
        if daraja.daraja == joriy_daraja_raqam:
            joriy_daraja = daraja
            if i + 1 < len(darajalar):
                keyingi_daraja = darajalar[i + 1]
            break
    
    keyingi_darajaga_ball = 0
    rivojlanish_foizi = 100.0
    
    if keyingi_daraja:
        keyingi_darajaga_ball = keyingi_daraja.kerakli_ball - joriy_ball
        if keyingi_daraja.kerakli_ball > joriy_daraja.kerakli_ball:
            rivojlanish_foizi = (
                (joriy_ball - joriy_daraja.kerakli_ball) /
                (keyingi_daraja.kerakli_ball - joriy_daraja.kerakli_ball)
            ) * 100
    
    return DarajaRivojlanishi(
        joriy_daraja=joriy_daraja,
        keyingi_daraja=keyingi_daraja,
        joriy_ball=joriy_ball,
        keyingi_darajaga_ball=max(0, keyingi_darajaga_ball),
        rivojlanish_foizi=min(100, max(0, rivojlanish_foizi))
    )
