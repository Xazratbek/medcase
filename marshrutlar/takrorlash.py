# MedCase Platform - Takrorlash Marshrutlari
# Spaced Repetition (SM-2) API endpointlari

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID

from sozlamalar.malumotlar_bazasi import sessiya_olish
from servislar.takrorlash_servisi import TakrorlashServisi
from sxemalar.takrorlash import (
    TakrorlashKartasiJavob, TakrorlashBaholash,
    BugungiTakrorlashlar, TakrorlashStatistikasi,
    TakrorlashTarixiJavob
)
from middleware.autentifikatsiya import joriy_foydalanuvchi_olish
from modellar.foydalanuvchi import Foydalanuvchi

router = APIRouter()


def karta_javobga(karta) -> TakrorlashKartasiJavob:
    """Kartani javob formatiga o'zgartirish."""
    return TakrorlashKartasiJavob(
        id=karta.id,
        foydalanuvchi_id=karta.foydalanuvchi_id,
        holat_id=karta.holat_id,
        easiness_factor=round(karta.easiness_factor, 2),
        interval=karta.interval,
        repetition=karta.repetition,
        oxirgi_takrorlash=karta.oxirgi_takrorlash,
        keyingi_takrorlash=karta.keyingi_takrorlash,
        jami_takrorlashlar=karta.jami_takrorlashlar,
        togri_javoblar=karta.togri_javoblar,
        oqilgan=karta.oqilgan,
        aniqlik_foizi=round(karta.aniqlik_foizi, 1),
        holat_sarlavhasi=getattr(karta, 'holat_sarlavhasi', None),
        holat_qiyinligi=getattr(karta, 'holat_qiyinligi', None),
        kategoriya_nomi=getattr(karta, 'kategoriya_nomi', None),
        yaratilgan_vaqt=karta.yaratilgan_vaqt,
        yangilangan_vaqt=karta.yangilangan_vaqt
    )


@router.get(
    "/bugungi",
    response_model=BugungiTakrorlashlar,
    summary="Bugungi takrorlashlar"
)
async def bugungi_takrorlashlar(
    limit: int = Query(50, ge=1, le=200),
    joriy_foydalanuvchi: Foydalanuvchi = Depends(joriy_foydalanuvchi_olish),
    db: AsyncSession = Depends(sessiya_olish)
):
    """Bugun takrorlash kerak bo'lgan kartalar."""
    servis = TakrorlashServisi(db)
    kartalar = await servis.bugungi_kartalar(joriy_foydalanuvchi.id, limit)
    
    return BugungiTakrorlashlar(
        kartalar=[karta_javobga(k) for k in kartalar],
        jami=len(kartalar),
        yangi=sum(1 for k in kartalar if k.repetition == 0),
        takrorlash_kerak=sum(1 for k in kartalar if k.repetition > 0),
        oqilgan=0
    )


@router.get(
    "/statistika",
    response_model=TakrorlashStatistikasi,
    summary="Takrorlash statistikasi"
)
async def takrorlash_statistikasi(
    joriy_foydalanuvchi: Foydalanuvchi = Depends(joriy_foydalanuvchi_olish),
    db: AsyncSession = Depends(sessiya_olish)
):
    """Takrorlash statistikasi."""
    servis = TakrorlashServisi(db)
    stat = await servis.statistika(joriy_foydalanuvchi.id)
    return TakrorlashStatistikasi(**stat)


@router.post(
    "/qoshish/{holat_id}",
    response_model=TakrorlashKartasiJavob,
    status_code=status.HTTP_201_CREATED,
    summary="Holatni takrorlashga qo'shish"
)
async def takrorlashga_qoshish(
    holat_id: UUID,
    joriy_foydalanuvchi: Foydalanuvchi = Depends(joriy_foydalanuvchi_olish),
    db: AsyncSession = Depends(sessiya_olish)
):
    """Holatni takrorlash kartasiga qo'shish."""
    servis = TakrorlashServisi(db)
    karta = await servis.holatni_takrorlashga_qoshish(
        joriy_foydalanuvchi.id, holat_id
    )
    return karta_javobga(karta)


@router.post(
    "/baholash/{holat_id}",
    response_model=TakrorlashKartasiJavob,
    summary="Takrorlash baholash (SM-2)"
)
async def takrorlash_baholash(
    holat_id: UUID,
    malumot: TakrorlashBaholash,
    joriy_foydalanuvchi: Foydalanuvchi = Depends(joriy_foydalanuvchi_olish),
    db: AsyncSession = Depends(sessiya_olish)
):
    """
    SM-2 algoritmi bilan takrorlash baholash.
    
    sifat qiymatlari:
    - 0: Umuman eslolmadim
    - 1: Noto'g'ri, lekin to'g'ri javobni ko'rganda esladim
    - 2: Noto'g'ri, lekin to'g'ri javob juda tanish
    - 3: To'g'ri, lekin qiyin bo'ldi
    - 4: To'g'ri, biroz o'ylab topdim
    - 5: To'g'ri, oson
    """
    servis = TakrorlashServisi(db)
    karta = await servis.baholash(joriy_foydalanuvchi.id, holat_id, malumot)
    return karta_javobga(karta)


@router.post(
    "/oqilgan/{holat_id}",
    response_model=TakrorlashKartasiJavob,
    summary="Kartani o'qilgan deb belgilash"
)
async def oqilgan_belgilash(
    holat_id: UUID,
    oqilgan: bool = Query(True),
    joriy_foydalanuvchi: Foydalanuvchi = Depends(joriy_foydalanuvchi_olish),
    db: AsyncSession = Depends(sessiya_olish)
):
    """Kartani o'qilgan/o'qilmagan deb belgilash."""
    servis = TakrorlashServisi(db)
    karta = await servis.kartani_oqilgan_qilish(
        joriy_foydalanuvchi.id, holat_id, oqilgan
    )
    
    if not karta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Karta topilmadi"
        )
    
    return karta_javobga(karta)


@router.get(
    "/tarix/{holat_id}",
    response_model=List[TakrorlashTarixiJavob],
    summary="Karta tarixi"
)
async def karta_tarixi(
    holat_id: UUID,
    limit: int = Query(20, ge=1, le=100),
    joriy_foydalanuvchi: Foydalanuvchi = Depends(joriy_foydalanuvchi_olish),
    db: AsyncSession = Depends(sessiya_olish)
):
    """Takrorlash tarixi."""
    servis = TakrorlashServisi(db)
    
    # Kartani olish
    karta = await servis.karta_olish_yoki_yaratish(
        joriy_foydalanuvchi.id, holat_id
    )
    
    tarix = await servis.karta_tarixi(karta.id, limit)
    
    return [
        TakrorlashTarixiJavob(
            id=t.id,
            karta_id=t.karta_id,
            sifat=t.sifat,
            togri=t.togri,
            sarflangan_vaqt=t.sarflangan_vaqt,
            ef_oldin=t.ef_oldin,
            ef_keyin=t.ef_keyin,
            interval_oldin=t.interval_oldin,
            interval_keyin=t.interval_keyin,
            yaratilgan_vaqt=t.yaratilgan_vaqt,
            yangilangan_vaqt=t.yangilangan_vaqt
        )
        for t in tarix
    ]


@router.get(
    "/kartalar",
    summary="Barcha kartalar"
)
async def barcha_kartalar(
    sahifa: int = Query(1, ge=1),
    hajm: int = Query(20, ge=1, le=100),
    faqat_bugungi: bool = Query(False),
    joriy_foydalanuvchi: Foydalanuvchi = Depends(joriy_foydalanuvchi_olish),
    db: AsyncSession = Depends(sessiya_olish)
):
    """Barcha kartalar ro'yxati."""
    servis = TakrorlashServisi(db)
    kartalar, jami = await servis.barcha_kartalar(
        joriy_foydalanuvchi.id, sahifa, hajm, faqat_bugungi
    )
    
    sahifalar_soni = (jami + hajm - 1) // hajm if hajm > 0 else 0
    
    return {
        "kartalar": [karta_javobga(k) for k in kartalar],
        "jami": jami,
        "sahifa": sahifa,
        "hajm": hajm,
        "sahifalar_soni": sahifalar_soni
    }
