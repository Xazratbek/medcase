# MedCase Platform - Kategoriya Marshrutlari
# Kategoriyalar, kichik kategoriyalar va bo'limlar

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID

from sozlamalar.malumotlar_bazasi import sessiya_olish
from servislar.kategoriya_servisi import KategoriyaServisi
from sozlamalar.redis_kesh import redis_kesh, KeshKalitlari
from sxemalar.kategoriya import (
    AsosiyKategoriyaJavob,
    AsosiyKategoriyaToliq,
    KichikKategoriyaJavob,
    KichikKategoriyaToliq,
    BolimJavob,
    KategoriyalarRoyxati,
    BolimJavob
)

router = APIRouter()


@router.get(
    "/toliq",
    summary="To'liq kategoriyalar ro'yxati (Admin uchun)"
)
async def toliq_kategoriyalar(
    db: AsyncSession = Depends(sessiya_olish)
):
    """
    Admin panel uchun to'liq kategoriyalar ierarxiyasi.
    Har bir kategoriya -> kichik kategoriyalar -> bo'limlar bilan.
    """
    servis = KategoriyaServisi(db)
    kategoriyalar = await servis.asosiy_kategoriyalar_olish(faol_faqat=False)

    natija = []
    for kat in kategoriyalar:
        kichik_kategoriyalar = []
        for kk in (kat.kichik_kategoriyalar or []):
            bolimlar = []
            jami_holatlar = 0
            for b in (kk.bolimlar or []):
                bolimlar.append({
                    "id": str(b.id),
                    "nomi": b.nomi,
                    "slug": b.slug,
                    "tavsif": b.tavsif,
                    "holatlar_soni": b.holatlar_soni or 0,
                    "tartib": b.tartib
                })
                jami_holatlar += (b.holatlar_soni or 0)

            kichik_kategoriyalar.append({
                "id": str(kk.id),
                "nomi": kk.nomi,
                "slug": kk.slug,
                "tavsif": kk.tavsif,
                "rang": kk.rang,
                "holatlar_soni": jami_holatlar,  # Calculated from bolimlar
                "bolimlar": bolimlar
            })

        natija.append({
            "id": str(kat.id),
            "nomi": kat.nomi,
            "slug": kat.slug,
            "tavsif": kat.tavsif,
            "rang": kat.rang,
            "ikonka": kat.ikonka,
            "holatlar_soni": kat.holatlar_soni or 0,
            "kichik_kategoriyalar": kichik_kategoriyalar
        })

    return {"kategoriyalar": natija}


@router.get(
    "/",
    response_model=KategoriyalarRoyxati,
    summary="Barcha kategoriyalar"
)
async def kategoriyalar_royxati(
    db: AsyncSession = Depends(sessiya_olish)
):
    """
    Barcha kategoriyalar, kichik kategoriyalar va bo'limlar
    ierarxiyasini qaytaradi.
    """
    kesh_kalit = f"{KeshKalitlari.KATEGORIYA}:royxat"
    keshlangan = await redis_kesh.olish(kesh_kalit)
    if keshlangan:
        return keshlangan

    servis = KategoriyaServisi(db)
    kategoriyalar = await servis.asosiy_kategoriyalar_olish()

    # Jami holatlar sonini hisoblash
    jami = sum(k.holatlar_soni or 0 for k in kategoriyalar)

    # Kategoriyalarni to'g'ri formatda qaytarish (bolimlar_soni hisoblash)
    natija = []
    for k in kategoriyalar:
        kichik_kategoriyalar = []
        for kk in (k.kichik_kategoriyalar or []):
            # Bo'limlardan jami holatlar sonini hisoblash
            sub_jami = sum(b.holatlar_soni or 0 for b in (kk.bolimlar or []))

            kichik_kategoriyalar.append(KichikKategoriyaJavob(
                id=kk.id,
                asosiy_kategoriya_id=kk.asosiy_kategoriya_id,
                nomi=kk.nomi,
                slug=kk.slug,
                tavsif=kk.tavsif,
                rasm_url=kk.rasm_url,
                rang=kk.rang,
                ikonka=kk.ikonka,
                tartib=kk.tartib,
                holatlar_soni=sub_jami, # Calculated from sections
                bolimlar_soni=len(kk.bolimlar) if kk.bolimlar else 0,
                faol=kk.faol,
                yaratilgan_vaqt=kk.yaratilgan_vaqt,
                yangilangan_vaqt=kk.yangilangan_vaqt
            ))

        natija.append(AsosiyKategoriyaToliq(
            id=k.id,
            nomi=k.nomi,
            slug=k.slug,
            tavsif=k.tavsif,
            rasm_url=k.rasm_url,
            rang=k.rang,
            ikonka=k.ikonka,
            tartib=k.tartib,
            holatlar_soni=k.holatlar_soni or 0,
            faol=k.faol,
            yaratilgan_vaqt=k.yaratilgan_vaqt,
            yangilangan_vaqt=k.yangilangan_vaqt,
            kichik_kategoriyalar=kichik_kategoriyalar
        ))

    natija = KategoriyalarRoyxati(
        asosiy_kategoriyalar=natija,
        jami_holatlar=jami
    )
    await redis_kesh.saqlash(kesh_kalit, natija.model_dump(), muddati=300)
    return natija


@router.get(
    "/asosiy",
    response_model=List[AsosiyKategoriyaJavob],
    summary="Asosiy kategoriyalar ro'yxati"
)
async def asosiy_kategoriyalar(
    db: AsyncSession = Depends(sessiya_olish)
):
    """
    Faqat asosiy kategoriyalar ro'yxatini qaytaradi.
    """
    kesh_kalit = f"{KeshKalitlari.KATEGORIYA}:asosiy"
    keshlangan = await redis_kesh.olish(kesh_kalit)
    if keshlangan:
        return keshlangan

    servis = KategoriyaServisi(db)
    natija = await servis.asosiy_kategoriyalar_olish()
    await redis_kesh.saqlash(kesh_kalit, [k.model_dump() for k in natija], muddati=300)
    return natija


@router.get(
    "/asosiy/{kategoriya_id}",
    response_model=AsosiyKategoriyaToliq,
    summary="Asosiy kategoriya tafsilotlari"
)
async def asosiy_kategoriya_olish(
    kategoriya_id: UUID,
    db: AsyncSession = Depends(sessiya_olish)
):
    """
    Asosiy kategoriyani kichik kategoriyalar bilan qaytaradi.
    """
    servis = KategoriyaServisi(db)
    kategoriya = await servis.asosiy_kategoriya_olish(kategoriya_id)

    if not kategoriya:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Kategoriya topilmadi"
        )

    return kategoriya


@router.get(
    "/asosiy/slug/{slug}",
    response_model=AsosiyKategoriyaToliq,
    summary="Slug bo'yicha asosiy kategoriya"
)
async def asosiy_kategoriya_slug_bilan(
    slug: str,
    db: AsyncSession = Depends(sessiya_olish)
):
    """
    Slug bo'yicha asosiy kategoriyani qaytaradi.
    """
    servis = KategoriyaServisi(db)
    kategoriya = await servis.asosiy_kategoriya_slug_bilan(slug)

    if not kategoriya:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Kategoriya topilmadi"
        )

    return kategoriya


@router.get(
    "/kichik/{asosiy_id}",
    response_model=List[KichikKategoriyaJavob],
    summary="Kichik kategoriyalar ro'yxati"
)
async def kichik_kategoriyalar(
    asosiy_id: UUID,
    db: AsyncSession = Depends(sessiya_olish)
):
    """
    Asosiy kategoriyaga tegishli kichik kategoriyalar.
    """
    servis = KategoriyaServisi(db)
    return await servis.kichik_kategoriyalar_olish(asosiy_id)


@router.get(
    "/kichik/detail/{kategoriya_id}",
    response_model=KichikKategoriyaToliq,
    summary="Kichik kategoriya tafsilotlari"
)
async def kichik_kategoriya_olish(
    kategoriya_id: UUID,
    db: AsyncSession = Depends(sessiya_olish)
):
    """
    Kichik kategoriyani bo'limlar bilan qaytaradi.
    """
    servis = KategoriyaServisi(db)
    kategoriya = await servis.kichik_kategoriya_olish(kategoriya_id)

    if not kategoriya:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Kategoriya topilmadi"
        )

    # bolimlar_soni ni qo'lda hisoblash (property Pydantic'da ishlamaydi)
    return KichikKategoriyaToliq(
        id=kategoriya.id,
        asosiy_kategoriya_id=kategoriya.asosiy_kategoriya_id,
        nomi=kategoriya.nomi,
        slug=kategoriya.slug,
        tavsif=kategoriya.tavsif,
        rasm_url=kategoriya.rasm_url,
        rang=kategoriya.rang,
        ikonka=kategoriya.ikonka,
        tartib=kategoriya.tartib,
        holatlar_soni=kategoriya.holatlar_soni or 0,
        bolimlar_soni=len(kategoriya.bolimlar) if kategoriya.bolimlar else 0,
        faol=kategoriya.faol,
        yaratilgan_vaqt=kategoriya.yaratilgan_vaqt,
        yangilangan_vaqt=kategoriya.yangilangan_vaqt,
        bolimlar=kategoriya.bolimlar or []
    )


@router.get(
    "/bolim/{kichik_kategoriya_id}",
    response_model=List[BolimJavob],
    summary="Bo'limlar ro'yxati"
)
async def bolimlar(
    kichik_kategoriya_id: UUID,
    db: AsyncSession = Depends(sessiya_olish)
):
    """
    Kichik kategoriyaga tegishli bo'limlar.
    """
    servis = KategoriyaServisi(db)
    return await servis.bolimlar_olish(kichik_kategoriya_id)


@router.get(
    "/bolim/detail/{bolim_id}",
    response_model=BolimJavob,
    summary="Bo'lim tafsilotlari"
)
async def bolim_olish(
    bolim_id: UUID,
    db: AsyncSession = Depends(sessiya_olish)
):
    """
    Bo'lim ma'lumotlarini qaytaradi.
    """
    servis = KategoriyaServisi(db)
    bolim = await servis.bolim_olish(bolim_id)

    if not bolim:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bo'lim topilmadi"
        )

    return bolim


@router.get(
    "/statistika",
    summary="Kategoriyalar statistikasi"
)
async def kategoriyalar_statistikasi(
    db: AsyncSession = Depends(sessiya_olish)
):
    """
    Kategoriyalar statistikasini qaytaradi.
    """
    servis = KategoriyaServisi(db)
    return await servis.toliq_statistika()
