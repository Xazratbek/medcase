# MedCase Platform - Izoh Marshrutlari
# Forum/Izohlar API endpointlari

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from uuid import UUID

from sozlamalar.malumotlar_bazasi import sessiya_olish
from servislar.izoh_servisi import IzohServisi
from sxemalar.izoh import (
    IzohYaratish, IzohYangilash, IzohJavob,
    IzohlarRoyxati, YoqtirishJavob, IzohFoydalanuvchi
)
from middleware.autentifikatsiya import (
    joriy_foydalanuvchi_olish,
    ixtiyoriy_foydalanuvchi
)
from modellar.foydalanuvchi import Foydalanuvchi

router = APIRouter()


def izoh_javobga(izoh, joriy_foydalanuvchi_id: UUID = None) -> dict:
    """Izohni javob formatiga o'zgartirish."""
    foydalanuvchi = None
    if izoh.foydalanuvchi:
        foydalanuvchi = IzohFoydalanuvchi(
            id=izoh.foydalanuvchi.id,
            foydalanuvchi_nomi=izoh.foydalanuvchi.foydalanuvchi_nomi,
            ism=izoh.foydalanuvchi.ism,
            familiya=izoh.foydalanuvchi.familiya,
            avatar_url=izoh.foydalanuvchi.profil.avatar_url if izoh.foydalanuvchi.profil else None
        )
    
    javoblar = []
    if hasattr(izoh, 'javoblar') and izoh.javoblar:
        for j in izoh.javoblar:
            if j.faol and j.moderatsiya_holati == "tasdiqlangan":
                javoblar.append(izoh_javobga(j, joriy_foydalanuvchi_id))
    
    yoqtirilgan = getattr(izoh, '_yoqtirilgan', False)
    
    return IzohJavob(
        id=izoh.id,
        holat_id=izoh.holat_id,
        foydalanuvchi_id=izoh.foydalanuvchi_id,
        foydalanuvchi=foydalanuvchi,
        ota_izoh_id=izoh.ota_izoh_id,
        matn=izoh.matn,
        yoqtirishlar_soni=izoh.yoqtirishlar_soni,
        javoblar_soni=izoh.javoblar_soni,
        tahrirlangan=izoh.tahrirlangan,
        yoqtirilgan=yoqtirilgan,
        javoblar=javoblar,
        yaratilgan_vaqt=izoh.yaratilgan_vaqt,
        yangilangan_vaqt=izoh.yangilangan_vaqt
    ).model_dump()


@router.post(
    "/",
    response_model=IzohJavob,
    status_code=status.HTTP_201_CREATED,
    summary="Izoh yaratish"
)
async def izoh_yaratish(
    malumot: IzohYaratish,
    joriy_foydalanuvchi: Foydalanuvchi = Depends(joriy_foydalanuvchi_olish),
    db: AsyncSession = Depends(sessiya_olish)
):
    """Yangi izoh yaratish."""
    servis = IzohServisi(db)
    izoh = await servis.yaratish(joriy_foydalanuvchi.id, malumot)
    
    # To'liq ma'lumot olish
    izoh = await servis.olish(izoh.id)
    return izoh_javobga(izoh, joriy_foydalanuvchi.id)


@router.get(
    "/holat/{holat_id}",
    response_model=IzohlarRoyxati,
    summary="Holat izohlari"
)
async def holat_izohlari(
    holat_id: UUID,
    sahifa: int = Query(1, ge=1),
    hajm: int = Query(20, ge=1, le=100),
    joriy_foydalanuvchi: Optional[Foydalanuvchi] = Depends(ixtiyoriy_foydalanuvchi),
    db: AsyncSession = Depends(sessiya_olish)
):
    """Holat izohlarini olish."""
    servis = IzohServisi(db)
    foydalanuvchi_id = joriy_foydalanuvchi.id if joriy_foydalanuvchi else None
    
    izohlar, jami = await servis.holat_izohlari(
        holat_id, foydalanuvchi_id, sahifa, hajm
    )
    
    sahifalar_soni = (jami + hajm - 1) // hajm if hajm > 0 else 0
    
    return IzohlarRoyxati(
        izohlar=[izoh_javobga(i, foydalanuvchi_id) for i in izohlar],
        jami=jami,
        sahifa=sahifa,
        hajm=hajm,
        sahifalar_soni=sahifalar_soni
    )


@router.put(
    "/{izoh_id}",
    response_model=IzohJavob,
    summary="Izoh yangilash"
)
async def izoh_yangilash(
    izoh_id: UUID,
    malumot: IzohYangilash,
    joriy_foydalanuvchi: Foydalanuvchi = Depends(joriy_foydalanuvchi_olish),
    db: AsyncSession = Depends(sessiya_olish)
):
    """Izohni yangilash (faqat o'z izohi)."""
    servis = IzohServisi(db)
    izoh = await servis.yangilash(izoh_id, joriy_foydalanuvchi.id, malumot)
    
    if not izoh:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Izoh topilmadi yoki sizga tegishli emas"
        )
    
    izoh = await servis.olish(izoh_id)
    return izoh_javobga(izoh, joriy_foydalanuvchi.id)


@router.delete(
    "/{izoh_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Izoh o'chirish"
)
async def izoh_ochirish(
    izoh_id: UUID,
    joriy_foydalanuvchi: Foydalanuvchi = Depends(joriy_foydalanuvchi_olish),
    db: AsyncSession = Depends(sessiya_olish)
):
    """Izohni o'chirish (faqat o'z izohi)."""
    servis = IzohServisi(db)
    admin = joriy_foydalanuvchi.admin_ekanligini_tekshirish
    
    natija = await servis.ochirish(izoh_id, joriy_foydalanuvchi.id, admin)
    
    if not natija:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Izoh topilmadi yoki sizga tegishli emas"
        )


@router.post(
    "/{izoh_id}/yoqtirish",
    response_model=YoqtirishJavob,
    summary="Izohni yoqtirish"
)
async def izoh_yoqtirish(
    izoh_id: UUID,
    joriy_foydalanuvchi: Foydalanuvchi = Depends(joriy_foydalanuvchi_olish),
    db: AsyncSession = Depends(sessiya_olish)
):
    """Izohni yoqtirish/yoqtirmaydigan qilish."""
    servis = IzohServisi(db)
    yoqtirilgan, soni = await servis.yoqtirish(izoh_id, joriy_foydalanuvchi.id)
    
    return YoqtirishJavob(yoqtirilgan=yoqtirilgan, yoqtirishlar_soni=soni)


@router.get(
    "/mening",
    response_model=IzohlarRoyxati,
    summary="Mening izohlarim"
)
async def mening_izohlarim(
    sahifa: int = Query(1, ge=1),
    hajm: int = Query(20, ge=1, le=100),
    joriy_foydalanuvchi: Foydalanuvchi = Depends(joriy_foydalanuvchi_olish),
    db: AsyncSession = Depends(sessiya_olish)
):
    """Joriy foydalanuvchi izohlari."""
    servis = IzohServisi(db)
    izohlar, jami = await servis.foydalanuvchi_izohlari(
        joriy_foydalanuvchi.id, sahifa, hajm
    )
    
    sahifalar_soni = (jami + hajm - 1) // hajm if hajm > 0 else 0
    
    return IzohlarRoyxati(
        izohlar=[izoh_javobga(i, joriy_foydalanuvchi.id) for i in izohlar],
        jami=jami,
        sahifa=sahifa,
        hajm=hajm,
        sahifalar_soni=sahifalar_soni
    )
