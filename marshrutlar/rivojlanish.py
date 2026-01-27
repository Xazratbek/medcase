# MedCase Platform - Rivojlanish Marshrutlari
# Foydalanuvchi rivojlanishi va statistika

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, desc, Integer
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import date, timedelta
import random

from sozlamalar.malumotlar_bazasi import sessiya_olish
from servislar.rivojlanish_servisi import RivojlanishServisi
from sxemalar.rivojlanish import (
    RivojlanishJavob,
    UrinishJavob,
    UrinishlarRoyxati,
    KunlikStatistikaJavob,
    HaftalikStatistika,
    SessiyaJavob,
    DashboardStatistika
)
from middleware.autentifikatsiya import joriy_foydalanuvchi_olish
from modellar.foydalanuvchi import Foydalanuvchi
from modellar.holat import Holat, QiyinlikDarajasi
from modellar.kategoriya import Bolim, KichikKategoriya, AsosiyKategoriya
from modellar.rivojlanish import HolatUrinishi, BolimRivojlanishi, FoydalanuvchiRivojlanishi, KunlikStatistika

router = APIRouter()


@router.get(
    "/",
    response_model=RivojlanishJavob,
    summary="Umumiy rivojlanish"
)
async def rivojlanish_olish(
    joriy_foydalanuvchi: Foydalanuvchi = Depends(joriy_foydalanuvchi_olish),
    db: AsyncSession = Depends(sessiya_olish)
):
    """
    Foydalanuvchining umumiy rivojlanish ma'lumotlarini qaytaradi.
    """
    servis = RivojlanishServisi(db)
    rivojlanish = await servis.rivojlanish_olish(joriy_foydalanuvchi.id)

    if not rivojlanish:
        # Yangi foydalanuvchi uchun bo'sh rivojlanish
        return RivojlanishJavob(
            id=joriy_foydalanuvchi.id,
            foydalanuvchi_id=joriy_foydalanuvchi.id
        )

    return rivojlanish


@router.get(
    "/dashboard",
    response_model=DashboardStatistika,
    summary="Dashboard statistikasi"
)
async def dashboard_statistika(
    joriy_foydalanuvchi: Foydalanuvchi = Depends(joriy_foydalanuvchi_olish),
    db: AsyncSession = Depends(sessiya_olish)
):
    """
    Dashboard uchun qisqacha statistika.
    """
    servis = RivojlanishServisi(db)
    rivojlanish = await servis.rivojlanish_olish(joriy_foydalanuvchi.id)

    # Bugungi statistika
    bugun = date.today()
    kunlik_sorov = select(KunlikStatistika).where(
        and_(
            KunlikStatistika.foydalanuvchi_id == joriy_foydalanuvchi.id,
            KunlikStatistika.sana == bugun
        )
    )
    kunlik_natija = await db.execute(kunlik_sorov)
    kunlik = kunlik_natija.scalar_one_or_none()

    # Haftalik vaqt
    hafta_boshi = bugun - timedelta(days=bugun.weekday())
    haftalik_sorov = select(KunlikStatistika).where(
        and_(
            KunlikStatistika.foydalanuvchi_id == joriy_foydalanuvchi.id,
            KunlikStatistika.sana >= hafta_boshi
        )
    )
    haftalik_natija = await db.execute(haftalik_sorov)
    haftalik = haftalik_natija.scalars().all()
    haftalik_vaqt = sum((k.jami_vaqt or 0) for k in haftalik) // 60  # daqiqaga

    # Oxirgi urinishlar
    urinishlar, _ = await servis.urinishlar_olish(
        joriy_foydalanuvchi.id, sahifa=1, hajm=5
    )

    # Kunlik maqsad
    kunlik_maqsad = 10
    if joriy_foydalanuvchi.profil:
        kunlik_maqsad = joriy_foydalanuvchi.profil.kunlik_maqsad

    # Kategoriya statistikasi
    kategoriya_stat_query = select(
        AsosiyKategoriya.nomi,
        func.count(HolatUrinishi.id).label('total')
    ).select_from(HolatUrinishi).join(
        Holat, HolatUrinishi.holat_id == Holat.id
    ).join(
        Bolim, Holat.bolim_id == Bolim.id
    ).join(
        KichikKategoriya, Bolim.kichik_kategoriya_id == KichikKategoriya.id
    ).join(
        AsosiyKategoriya, KichikKategoriya.asosiy_kategoriya_id == AsosiyKategoriya.id
    ).where(
        HolatUrinishi.foydalanuvchi_id == joriy_foydalanuvchi.id
    ).group_by(AsosiyKategoriya.nomi).order_by(desc('total'))

    kategoriya_stat_result = await db.execute(kategoriya_stat_query)
    kategoriya_stats = kategoriya_stat_result.all()

    eng_kop_yechilgan_kategoriya = kategoriya_stats[0].nomi if kategoriya_stats else None
    eng_kam_yechilgan_kategoriya = kategoriya_stats[-1].nomi if kategoriya_stats else None

    return DashboardStatistika(
        jami_holatlar=rivojlanish.jami_urinishlar if rivojlanish else 0,
        aniqlik_foizi=rivojlanish.aniqlik_foizi if rivojlanish else 0,
        bu_hafta_vaqt=haftalik_vaqt,
        daraja=rivojlanish.daraja if rivojlanish else 1,
        joriy_streak=rivojlanish.joriy_streak if rivojlanish else 0,
        bugungi_holatlar=kunlik.yechilgan_holatlar if kunlik else 0,
        kunlik_maqsad=kunlik_maqsad,
        oxirgi_urinishlar=urinishlar,
        jami_yechilgan_holatlar=rivojlanish.jami_urinishlar if rivojlanish else 0,
        ortacha_aniqlik=rivojlanish.aniqlik_foizi if rivojlanish else 0,
        eng_kop_yechilgan_kategoriya=eng_kop_yechilgan_kategoriya,
        eng_kam_yechilgan_kategoriya=eng_kam_yechilgan_kategoriya,
    )


@router.get(
    "/urinishlar",
    response_model=UrinishlarRoyxati,
    summary="Urinishlar tarixi"
)
async def urinishlar_tarixi(
    sahifa: int = Query(1, ge=1),
    hajm: int = Query(20, ge=1, le=100),
    joriy_foydalanuvchi: Foydalanuvchi = Depends(joriy_foydalanuvchi_olish),
    db: AsyncSession = Depends(sessiya_olish)
):
    """
    Foydalanuvchining barcha urinishlar tarixini qaytaradi.
    """
    servis = RivojlanishServisi(db)
    urinishlar, jami = await servis.urinishlar_olish(
        joriy_foydalanuvchi.id, sahifa, hajm
    )

    return UrinishlarRoyxati(
        urinishlar=urinishlar,
        jami=jami,
        sahifa=sahifa,
        hajm=hajm
    )


@router.get(
    "/kunlik",
    response_model=List[KunlikStatistikaJavob],
    summary="Kunlik statistika"
)
async def kunlik_statistika(
    kunlar: int = Query(30, ge=1, le=365),
    joriy_foydalanuvchi: Foydalanuvchi = Depends(joriy_foydalanuvchi_olish),
    db: AsyncSession = Depends(sessiya_olish)
):
    """
    Oxirgi N kun uchun kunlik statistikani qaytaradi.
    """
    from sqlalchemy import select, and_
    from modellar.rivojlanish import KunlikStatistika

    bugun = date.today()
    boshlanish = bugun - timedelta(days=kunlar)

    sorov = select(KunlikStatistika).where(
        and_(
            KunlikStatistika.foydalanuvchi_id == joriy_foydalanuvchi.id,
            KunlikStatistika.sana >= boshlanish
        )
    ).order_by(KunlikStatistika.sana.desc())

    natija = await db.execute(sorov)
    return natija.scalars().all()


@router.post(
    "/sessiya/boshlash",
    response_model=SessiyaJavob,
    summary="O'qish sessiyasini boshlash"
)
async def sessiya_boshlash(
    qurilma_turi: Optional[str] = None,
    joriy_foydalanuvchi: Foydalanuvchi = Depends(joriy_foydalanuvchi_olish),
    db: AsyncSession = Depends(sessiya_olish)
):
    """
    Yangi o'qish sessiyasini boshlaydi.
    """
    servis = RivojlanishServisi(db)
    sessiya = await servis.sessiya_boshlash(
        joriy_foydalanuvchi.id,
        qurilma_turi
    )
    return sessiya


@router.post(
    "/sessiya/{sessiya_id}/tugatish",
    response_model=SessiyaJavob,
    summary="O'qish sessiyasini tugatish"
)
async def sessiya_tugatish(
    sessiya_id: UUID,
    joriy_foydalanuvchi: Foydalanuvchi = Depends(joriy_foydalanuvchi_olish),
    db: AsyncSession = Depends(sessiya_olish)
):
    """
    O'qish sessiyasini tugatadi.
    """
    servis = RivojlanishServisi(db)
    sessiya = await servis.sessiya_tugatish(sessiya_id)

    if not sessiya:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sessiya topilmadi"
        )

    return sessiya


# ============== Zaif Tomonlar ==============

@router.get(
    "/zaif-tomonlar",
    summary="Zaif tomonlar"
)
async def zaif_tomonlar_olish(
    limit: int = Query(5, ge=1, le=20),
    joriy_foydalanuvchi: Foydalanuvchi = Depends(joriy_foydalanuvchi_olish),
    db: AsyncSession = Depends(sessiya_olish)
) -> List[Dict[str, Any]]:
    """
    Foydalanuvchining zaif tomonlarini (past aniqlikli kategoriyalar) qaytaradi.
    Minimum 3 ta urinish bo'lgan kategoriyalar hisobga olinadi.
    """
    # Kategoriya bo'yicha statistika olish
    sorov = select(
        AsosiyKategoriya.id,
        AsosiyKategoriya.nomi,
        func.count(HolatUrinishi.id).label('jami'),
        func.sum(func.cast(HolatUrinishi.togri, Integer)).label('togri')
    ).select_from(HolatUrinishi).join(
        Holat, HolatUrinishi.holat_id == Holat.id
    ).join(
        Bolim, Holat.bolim_id == Bolim.id
    ).join(
        KichikKategoriya, Bolim.kichik_kategoriya_id == KichikKategoriya.id
    ).join(
        AsosiyKategoriya, KichikKategoriya.asosiy_kategoriya_id == AsosiyKategoriya.id
    ).where(
        HolatUrinishi.foydalanuvchi_id == joriy_foydalanuvchi.id
    ).group_by(
        AsosiyKategoriya.id, AsosiyKategoriya.nomi
    ).having(
        func.count(HolatUrinishi.id) >= 3  # Minimum 3 urinish
    )

    natija = await db.execute(sorov)
    rows = natija.all()

    # Aniqlik hisoblash va saralash
    zaif_tomonlar = []
    for row in rows:
        jami = row.jami or 0
        togri = row.togri or 0
        aniqlik = (togri / jami * 100) if jami > 0 else 0

        zaif_tomonlar.append({
            "kategoriya_id": str(row.id),
            "kategoriya": row.nomi,
            "jami_urinishlar": jami,
            "togri_javoblar": togri,
            "aniqlik": round(aniqlik, 1)
        })

    # Aniqlik bo'yicha saralash (eng past birinchi)
    zaif_tomonlar.sort(key=lambda x: x["aniqlik"])

    # Faqat 70% dan past aniqlikli kategoriyalar
    zaif_tomonlar = [z for z in zaif_tomonlar if z["aniqlik"] < 70]

    return zaif_tomonlar[:limit]


# ============== Kuchli Tomonlar ==============

@router.get(
    "/kuchli-tomonlar",
    summary="Kuchli tomonlar"
)
async def kuchli_tomonlar_olish(
    limit: int = Query(5, ge=1, le=20),
    joriy_foydalanuvchi: Foydalanuvchi = Depends(joriy_foydalanuvchi_olish),
    db: AsyncSession = Depends(sessiya_olish)
) -> List[Dict[str, Any]]:
    """
    Foydalanuvchining kuchli tomonlarini (yuqori aniqlikli kategoriyalar) qaytaradi.
    """
    sorov = select(
        AsosiyKategoriya.id,
        AsosiyKategoriya.nomi,
        func.count(HolatUrinishi.id).label('jami'),
        func.sum(func.cast(HolatUrinishi.togri, Integer)).label('togri')
    ).select_from(HolatUrinishi).join(
        Holat, HolatUrinishi.holat_id == Holat.id
    ).join(
        Bolim, Holat.bolim_id == Bolim.id
    ).join(
        KichikKategoriya, Bolim.kichik_kategoriya_id == KichikKategoriya.id
    ).join(
        AsosiyKategoriya, KichikKategoriya.asosiy_kategoriya_id == AsosiyKategoriya.id
    ).where(
        HolatUrinishi.foydalanuvchi_id == joriy_foydalanuvchi.id
    ).group_by(
        AsosiyKategoriya.id, AsosiyKategoriya.nomi
    ).having(
        func.count(HolatUrinishi.id) >= 3
    )

    natija = await db.execute(sorov)
    rows = natija.all()

    kuchli_tomonlar = []
    for row in rows:
        jami = row.jami or 0
        togri = row.togri or 0
        aniqlik = (togri / jami * 100) if jami > 0 else 0

        kuchli_tomonlar.append({
            "kategoriya_id": str(row.id),
            "kategoriya": row.nomi,
            "jami_urinishlar": jami,
            "togri_javoblar": togri,
            "aniqlik": round(aniqlik, 1)
        })

    # Aniqlik bo'yicha teskari saralash (eng yuqori birinchi)
    kuchli_tomonlar.sort(key=lambda x: x["aniqlik"], reverse=True)

    # Faqat 70% dan yuqori aniqlikli kategoriyalar
    kuchli_tomonlar = [k for k in kuchli_tomonlar if k["aniqlik"] >= 70]

    return kuchli_tomonlar[:limit]


# ============== Kategoriya bo'yicha statistika ==============

@router.get(
    "/kategoriya-statistika",
    summary="Kategoriya bo'yicha statistika"
)
async def kategoriya_statistika(
    joriy_foydalanuvchi: Foydalanuvchi = Depends(joriy_foydalanuvchi_olish),
    db: AsyncSession = Depends(sessiya_olish)
) -> List[Dict[str, Any]]:
    """
    Barcha kategoriyalar bo'yicha foydalanuvchi statistikasi.
    """
    sorov = select(
        AsosiyKategoriya.id,
        AsosiyKategoriya.nomi,
        AsosiyKategoriya.rang,
        func.count(HolatUrinishi.id).label('jami'),
        func.sum(func.cast(HolatUrinishi.togri, Integer)).label('togri')
    ).select_from(HolatUrinishi).join(
        Holat, HolatUrinishi.holat_id == Holat.id
    ).join(
        Bolim, Holat.bolim_id == Bolim.id
    ).join(
        KichikKategoriya, Bolim.kichik_kategoriya_id == KichikKategoriya.id
    ).join(
        AsosiyKategoriya, KichikKategoriya.asosiy_kategoriya_id == AsosiyKategoriya.id
    ).where(
        HolatUrinishi.foydalanuvchi_id == joriy_foydalanuvchi.id
    ).group_by(
        AsosiyKategoriya.id, AsosiyKategoriya.nomi, AsosiyKategoriya.rang
    ).order_by(AsosiyKategoriya.nomi)

    natija = await db.execute(sorov)
    rows = natija.all()

    statistika = []
    for row in rows:
        jami = row.jami or 0
        togri = row.togri or 0
        aniqlik = (togri / jami * 100) if jami > 0 else 0

        statistika.append({
            "kategoriya_id": str(row.id),
            "kategoriya": row.nomi,
            "rang": row.rang,
            "jami_urinishlar": jami,
            "togri_javoblar": togri,
            "aniqlik": round(aniqlik, 1)
        })

    return statistika
