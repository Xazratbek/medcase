# MedCase Platform - Holat Marshrutlari
# Klinik holatlar boshqaruvi

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from uuid import UUID

from sozlamalar.malumotlar_bazasi import sessiya_olish
from servislar.holat_servisi import HolatServisi
from servislar.rivojlanish_servisi import RivojlanishServisi
from sxemalar.holat import (
    HolatJavob,
    HolatToliqJavob,
    HolatQidirish,
    HolatRoyxati,
    TegJavob
)
from sxemalar.rivojlanish import UrinishYaratish, UrinishJavob
from middleware.autentifikatsiya import (
    joriy_foydalanuvchi_olish,
    ixtiyoriy_foydalanuvchi
)
from modellar.foydalanuvchi import Foydalanuvchi
from modellar.holat import QiyinlikDarajasi, HolatTuri

router = APIRouter()


@router.get(
    "/",
    response_model=HolatRoyxati,
    summary="Holatlar ro'yxati"
)
async def holatlar_royxati(
    sahifa: int = Query(1, ge=1),
    hajm: int = Query(20, ge=1, le=100),
    bolim_id: Optional[UUID] = None,
    qiyinlik: Optional[QiyinlikDarajasi] = None,
    turi: Optional[HolatTuri] = None,
    qidiruv: Optional[str] = None,
    joriy_foydalanuvchi: Optional[Foydalanuvchi] = Depends(ixtiyoriy_foydalanuvchi),
    db: AsyncSession = Depends(sessiya_olish)
):
    """
    Holatlar ro'yxatini qaytaradi. Filtrlar bilan qidirish mumkin.
    """
    servis = HolatServisi(db)
    
    qidiruv_malumot = HolatQidirish(
        sahifa=sahifa,
        hajm=hajm,
        bolim_id=bolim_id,
        qiyinlik=qiyinlik,
        turi=turi,
        qidiruv=qidiruv
    )
    
    foydalanuvchi_id = joriy_foydalanuvchi.id if joriy_foydalanuvchi else None
    holatlar, jami = await servis.qidirish(qidiruv_malumot, foydalanuvchi_id)
    
    sahifalar_soni = (jami + hajm - 1) // hajm if hajm > 0 else 0
    
    return HolatRoyxati(
        holatlar=holatlar,
        jami=jami,
        sahifa=sahifa,
        hajm=hajm,
        sahifalar_soni=sahifalar_soni
    )


@router.get(
    "/tasodifiy",
    response_model=List[HolatJavob],
    summary="Tasodifiy holatlar"
)
async def tasodifiy_holatlar(
    soni: int = Query(10, ge=1, le=50),
    bolim_id: Optional[UUID] = None,
    qiyinlik: Optional[QiyinlikDarajasi] = None,
    db: AsyncSession = Depends(sessiya_olish)
):
    """
    Tasodifiy holatlar ro'yxatini qaytaradi.
    """
    servis = HolatServisi(db)
    holatlar = await servis.tasodifiy_olish(
        soni=soni,
        bolim_id=bolim_id,
        qiyinlik=qiyinlik
    )
    return holatlar


@router.get(
    "/bolim/{bolim_id}",
    response_model=HolatRoyxati,
    summary="Bo'lim bo'yicha holatlar"
)
async def bolim_holatlari(
    bolim_id: UUID,
    sahifa: int = Query(1, ge=1),
    hajm: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(sessiya_olish)
):
    """
    Bo'limga tegishli holatlar ro'yxati.
    """
    servis = HolatServisi(db)
    holatlar, jami = await servis.bolim_boyicha(bolim_id, sahifa, hajm)
    
    sahifalar_soni = (jami + hajm - 1) // hajm if hajm > 0 else 0
    
    return HolatRoyxati(
        holatlar=holatlar,
        jami=jami,
        sahifa=sahifa,
        hajm=hajm,
        sahifalar_soni=sahifalar_soni
    )


@router.get(
    "/teglar",
    response_model=List[TegJavob],
    summary="Teglar ro'yxati"
)
async def teglar_royxati(
    db: AsyncSession = Depends(sessiya_olish)
):
    """
    Barcha teglar ro'yxati.
    """
    servis = HolatServisi(db)
    return await servis.teglar_olish()


@router.get(
    "/kunlik",
    response_model=HolatJavob,
    summary="Kunlik holat (Daily Challenge)"
)
async def kunlik_holat(
    db: AsyncSession = Depends(sessiya_olish)
):
    """
    Kunlik challenge holatini qaytaradi.
    Har kuni tasodifiy holat tanlanadi va kun davomida saqlanadi.
    """
    from datetime import date
    from sozlamalar.redis_kesh import redis_kesh
    import json
    
    bugun = date.today().isoformat()
    kesh_kaliti = f"kunlik_holat:{bugun}"
    
    # Keshdan tekshirish
    keshdan = await redis_kesh.olish(kesh_kaliti)
    if keshdan:
        holat_id = keshdan
        servis = HolatServisi(db)
        holat = await servis.olish(UUID(holat_id))
        if holat:
            return holat
    
    # Yangi kunlik holat tanlash (o'rtacha yoki qiyin)
    servis = HolatServisi(db)
    holatlar = await servis.tasodifiy_olish(
        soni=1,
        qiyinlik=None  # Barcha qiyinlikdan
    )
    
    if not holatlar:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Kunlik holat topilmadi. Holatlar mavjud emas."
        )
    
    holat = holatlar[0]
    
    # 24 soatga keshlash
    await redis_kesh.saqlash(
        kesh_kaliti,
        str(holat.id),
        muddati=86400  # 24 soat
    )
    
    return holat


@router.get(
    "/{holat_id}",
    response_model=HolatJavob,
    summary="Holat ma'lumotlari"
)
async def holat_olish(
    holat_id: UUID,
    db: AsyncSession = Depends(sessiya_olish)
):
    """
    Holat ma'lumotlarini qaytaradi (javoblarsiz).
    """
    servis = HolatServisi(db)
    holat = await servis.olish(holat_id)
    
    if not holat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Holat topilmadi"
        )
    
    if not holat.chop_etilgan:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bu holat hali chop etilmagan"
        )
    
    return holat


@router.post(
    "/{holat_id}/javob",
    response_model=UrinishJavob,
    summary="Holatga javob berish"
)
async def javob_berish(
    holat_id: UUID,
    tanlangan_javob: str = Query(..., pattern="^[A-Da-d]$"),
    sarflangan_vaqt: int = Query(..., ge=0),
    sessiya_id: Optional[UUID] = None,
    joriy_foydalanuvchi: Foydalanuvchi = Depends(joriy_foydalanuvchi_olish),
    db: AsyncSession = Depends(sessiya_olish)
):
    """
    Holatga javob berish va natijani olish.
    """
    # Holatni tekshirish
    holat_servis = HolatServisi(db)
    holat = await holat_servis.olish(holat_id)
    
    if not holat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Holat topilmadi"
        )
    
    # Urinish yaratish
    rivojlanish_servis = RivojlanishServisi(db)
    urinish_malumot = UrinishYaratish(
        holat_id=holat_id,
        tanlangan_javob=tanlangan_javob.upper(),
        sarflangan_vaqt=sarflangan_vaqt,
        sessiya_id=sessiya_id
    )
    
    urinish = await rivojlanish_servis.urinish_yaratish(
        joriy_foydalanuvchi.id,
        urinish_malumot
    )
    
    # Holat statistikasini yangilash
    await holat_servis.statistika_yangilash(holat_id, urinish.togri)
    
    # Reytingni yangilash (har 10 ta urinishdan keyin, yoki to'g'ri javobda)
    if urinish.togri:
        from servislar.gamifikatsiya_servisi import GamifikatsiyaServisi
        try:
            gam_servis = GamifikatsiyaServisi(db)
            await gam_servis.reyting_yangilash("global")
        except Exception:
            pass  # Reyting yangilash xatosi javobga ta'sir qilmasligi kerak
    
    return urinish


@router.get(
    "/{holat_id}/javob",
    response_model=HolatToliqJavob,
    summary="Holat javoblari bilan"
)
async def holat_javoblari(
    holat_id: UUID,
    joriy_foydalanuvchi: Foydalanuvchi = Depends(joriy_foydalanuvchi_olish),
    db: AsyncSession = Depends(sessiya_olish)
):
    """
    Holat to'g'ri javob va tushuntirishlar bilan.
    Faqat javob bergandan keyin ko'rish mumkin.
    """
    holat_servis = HolatServisi(db)
    holat = await holat_servis.olish(holat_id)
    
    if not holat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Holat topilmadi"
        )
    
    # Foydalanuvchi javob berganligini tekshirish
    rivojlanish_servis = RivojlanishServisi(db)
    from sqlalchemy import select, and_
    from modellar.rivojlanish import HolatUrinishi
    
    sorov = select(HolatUrinishi).where(
        and_(
            HolatUrinishi.foydalanuvchi_id == joriy_foydalanuvchi.id,
            HolatUrinishi.holat_id == holat_id
        )
    )
    natija = await db.execute(sorov)
    urinish = natija.scalar_one_or_none()
    
    if not urinish:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Avval holatga javob bering"
        )
    
    return HolatToliqJavob(
        **holat.__dict__,
        togri_javob=holat.togri_javob,
        umumiy_tushuntirish=holat.umumiy_tushuntirish
    )
