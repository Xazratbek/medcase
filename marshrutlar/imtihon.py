# MedCase Platform - Imtihon Marshrutlari
# Timer rejimi va imtihon simulyatsiyasi API endpointlari

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID

from sozlamalar.malumotlar_bazasi import sessiya_olish
from servislar.imtihon_servisi import ImtihonServisi
from sxemalar.imtihon import (
    ImtihonShabloniYaratish, ImtihonShabloniJavob,
    ImtihonBoshlash, ImtihonSavoli, ImtihonSavolJavob,
    ImtihonHolatiJavob, ImtihonNatijasi, ImtihonlarRoyxati,
    ImtihonStatistikasi
)
from middleware.autentifikatsiya import joriy_foydalanuvchi_olish
from modellar.foydalanuvchi import Foydalanuvchi
from modellar.imtihon import ImtihonHolati

router = APIRouter()


def imtihon_holatiga(imtihon) -> ImtihonHolatiJavob:
    """Imtihonni holat formatiga o'zgartirish."""
    return ImtihonHolatiJavob(
        id=imtihon.id,
        foydalanuvchi_id=imtihon.foydalanuvchi_id,
        nom=imtihon.nom,
        turi=imtihon.turi,
        holat=imtihon.holat,
        umumiy_vaqt=imtihon.umumiy_vaqt,
        savol_vaqti=imtihon.savol_vaqti,
        qolgan_vaqt=imtihon.qolgan_vaqt,
        boshlangan_vaqt=imtihon.boshlangan_vaqt,
        jami_savollar=imtihon.jami_savollar,
        joriy_savol_indeksi=imtihon.joriy_savol_indeksi,
        javob_berilgan=imtihon.javob_berilgan,
        togri_javoblar=imtihon.togri_javoblar,
        notogri_javoblar=imtihon.notogri_javoblar,
        otkazilgan_savollar=imtihon.otkazilgan_savollar,
        orqaga_qaytish=imtihon.orqaga_qaytish,
        aralashtirish=imtihon.aralashtirish
    )


def imtihon_natijasiga(imtihon, javoblar_bilan: bool = False) -> ImtihonNatijasi:
    """Imtihonni natija formatiga o'zgartirish."""
    javoblar = []
    if javoblar_bilan and hasattr(imtihon, 'javoblar') and imtihon.javoblar:
        from sxemalar.imtihon import ImtihonJavobi
        for j in imtihon.javoblar:
            javoblar.append(ImtihonJavobi(
                id=j.id,
                imtihon_id=j.imtihon_id,
                holat_id=j.holat_id,
                savol_indeksi=j.savol_indeksi,
                tanlangan_javob=j.tanlangan_javob,
                togri_javob=j.togri_javob,
                togri=j.togri,
                sarflangan_vaqt=j.sarflangan_vaqt,
                otkazilgan=j.otkazilgan,
                belgilangan=j.belgilangan
            ))
    
    return ImtihonNatijasi(
        id=imtihon.id,
        foydalanuvchi_id=imtihon.foydalanuvchi_id,
        nom=imtihon.nom,
        turi=imtihon.turi,
        holat=imtihon.holat,
        boshlangan_vaqt=imtihon.boshlangan_vaqt,
        tugallangan_vaqt=imtihon.tugallangan_vaqt,
        sarflangan_vaqt=imtihon.sarflangan_vaqt,
        jami_savollar=imtihon.jami_savollar,
        javob_berilgan=imtihon.javob_berilgan,
        togri_javoblar=imtihon.togri_javoblar,
        notogri_javoblar=imtihon.notogri_javoblar,
        otkazilgan_savollar=imtihon.otkazilgan_savollar,
        ball_foizi=imtihon.ball_foizi,
        otish_balli=imtihon.otish_balli,
        otgan=imtihon.otgan,
        javoblar=javoblar,
        yaratilgan_vaqt=imtihon.yaratilgan_vaqt,
        yangilangan_vaqt=imtihon.yangilangan_vaqt
    )


# ============== Shablonlar ==============

@router.get(
    "/shablonlar",
    response_model=List[ImtihonShabloniJavob],
    summary="Imtihon shablonlari"
)
async def shablonlar_royxati(
    sahifa: int = Query(1, ge=1),
    hajm: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(sessiya_olish)
):
    """Imtihon shablonlari ro'yxati."""
    servis = ImtihonServisi(db)
    shablonlar, _ = await servis.shablonlar_royxati(sahifa, hajm)
    
    return [
        ImtihonShabloniJavob(
            id=s.id,
            nom=s.nom,
            tavsif=s.tavsif,
            turi=s.turi,
            savollar_soni=s.savollar_soni,
            umumiy_vaqt=s.umumiy_vaqt,
            savol_vaqti=s.savol_vaqti,
            oson_foiz=s.oson_foiz,
            ortacha_foiz=s.ortacha_foiz,
            qiyin_foiz=s.qiyin_foiz,
            kategoriya_idlari=s.kategoriya_idlari,
            bolim_idlari=s.bolim_idlari,
            aralashtirish=s.aralashtirish,
            javob_aralashtirish=s.javob_aralashtirish,
            orqaga_qaytish=s.orqaga_qaytish,
            natijani_korsatish=s.natijani_korsatish,
            otish_balli=s.otish_balli,
            otkazilgan_soni=s.otkazilgan_soni,
            ortacha_ball=s.ortacha_ball,
            yaratilgan_vaqt=s.yaratilgan_vaqt,
            yangilangan_vaqt=s.yangilangan_vaqt
        )
        for s in shablonlar
    ]


@router.get(
    "/shablon/{shablon_id}",
    response_model=ImtihonShabloniJavob,
    summary="Shablon olish"
)
async def shablon_olish(
    shablon_id: UUID,
    db: AsyncSession = Depends(sessiya_olish)
):
    """Bitta shablonni olish."""
    servis = ImtihonServisi(db)
    shablon = await servis.shablon_olish(shablon_id)
    
    if not shablon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shablon topilmadi"
        )
    
    return ImtihonShabloniJavob(
        id=shablon.id,
        nom=shablon.nom,
        tavsif=shablon.tavsif,
        turi=shablon.turi,
        savollar_soni=shablon.savollar_soni,
        umumiy_vaqt=shablon.umumiy_vaqt,
        savol_vaqti=shablon.savol_vaqti,
        oson_foiz=shablon.oson_foiz,
        ortacha_foiz=shablon.ortacha_foiz,
        qiyin_foiz=shablon.qiyin_foiz,
        kategoriya_idlari=shablon.kategoriya_idlari,
        bolim_idlari=shablon.bolim_idlari,
        aralashtirish=shablon.aralashtirish,
        javob_aralashtirish=shablon.javob_aralashtirish,
        orqaga_qaytish=shablon.orqaga_qaytish,
        natijani_korsatish=shablon.natijani_korsatish,
        otish_balli=shablon.otish_balli,
        otkazilgan_soni=shablon.otkazilgan_soni,
        ortacha_ball=shablon.ortacha_ball,
        yaratilgan_vaqt=shablon.yaratilgan_vaqt,
        yangilangan_vaqt=shablon.yangilangan_vaqt
    )


# ============== Imtihon operatsiyalari ==============

@router.post(
    "/boshlash",
    response_model=ImtihonHolatiJavob,
    status_code=status.HTTP_201_CREATED,
    summary="Imtihon boshlash"
)
async def imtihon_boshlash(
    malumot: ImtihonBoshlash,
    joriy_foydalanuvchi: Foydalanuvchi = Depends(joriy_foydalanuvchi_olish),
    db: AsyncSession = Depends(sessiya_olish)
):
    """
    Yangi imtihon boshlash.
    
    - shablon_id: Tayyor shablondan boshlash
    - yoki: turi, savollar_soni, umumiy_vaqt kabi parametrlar
    """
    servis = ImtihonServisi(db)
    
    try:
        imtihon = await servis.boshlash(joriy_foydalanuvchi.id, malumot)
        await db.commit()
        return imtihon_holatiga(imtihon)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "/{imtihon_id}",
    response_model=ImtihonHolatiJavob,
    summary="Imtihon holati"
)
async def imtihon_olish(
    imtihon_id: UUID,
    joriy_foydalanuvchi: Foydalanuvchi = Depends(joriy_foydalanuvchi_olish),
    db: AsyncSession = Depends(sessiya_olish)
):
    """Imtihon holatini olish."""
    servis = ImtihonServisi(db)
    imtihon = await servis.olish(imtihon_id, joriy_foydalanuvchi.id)
    
    if not imtihon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Imtihon topilmadi"
        )
    
    return imtihon_holatiga(imtihon)


@router.get(
    "/{imtihon_id}/savol",
    response_model=ImtihonSavoli,
    summary="Joriy savol"
)
async def joriy_savol(
    imtihon_id: UUID,
    joriy_foydalanuvchi: Foydalanuvchi = Depends(joriy_foydalanuvchi_olish),
    db: AsyncSession = Depends(sessiya_olish)
):
    """Joriy savolni olish."""
    servis = ImtihonServisi(db)
    savol = await servis.joriy_savol(imtihon_id, joriy_foydalanuvchi.id)
    
    if not savol:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Savol topilmadi yoki imtihon yakunlangan"
        )
    
    return ImtihonSavoli(**savol)


@router.post(
    "/{imtihon_id}/javob",
    summary="Javob berish"
)
async def javob_berish(
    imtihon_id: UUID,
    malumot: ImtihonSavolJavob,
    joriy_foydalanuvchi: Foydalanuvchi = Depends(joriy_foydalanuvchi_olish),
    db: AsyncSession = Depends(sessiya_olish)
):
    """Savolga javob berish."""
    servis = ImtihonServisi(db)
    
    try:
        natija = await servis.javob_berish(
            imtihon_id, joriy_foydalanuvchi.id, malumot
        )
        await db.commit()
        return natija
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post(
    "/{imtihon_id}/keyingi",
    response_model=ImtihonSavoli,
    summary="Keyingi savol"
)
async def keyingi_savol(
    imtihon_id: UUID,
    joriy_foydalanuvchi: Foydalanuvchi = Depends(joriy_foydalanuvchi_olish),
    db: AsyncSession = Depends(sessiya_olish)
):
    """Keyingi savolga o'tish."""
    servis = ImtihonServisi(db)
    savol = await servis.keyingi_savol(imtihon_id, joriy_foydalanuvchi.id)
    
    if not savol:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Keyingi savol yo'q yoki imtihon yakunlangan"
        )
    
    await db.commit()
    return ImtihonSavoli(**savol)


@router.post(
    "/{imtihon_id}/oldingi",
    response_model=ImtihonSavoli,
    summary="Oldingi savol"
)
async def oldingi_savol(
    imtihon_id: UUID,
    joriy_foydalanuvchi: Foydalanuvchi = Depends(joriy_foydalanuvchi_olish),
    db: AsyncSession = Depends(sessiya_olish)
):
    """Oldingi savolga qaytish."""
    servis = ImtihonServisi(db)
    savol = await servis.oldingi_savol(imtihon_id, joriy_foydalanuvchi.id)
    
    if not savol:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Oldingi savol yo'q yoki orqaga qaytish ruxsati yo'q"
        )
    
    await db.commit()
    return ImtihonSavoli(**savol)


@router.post(
    "/{imtihon_id}/otish/{savol_indeksi}",
    response_model=ImtihonSavoli,
    summary="Savolga o'tish"
)
async def savolga_otish(
    imtihon_id: UUID,
    savol_indeksi: int,
    joriy_foydalanuvchi: Foydalanuvchi = Depends(joriy_foydalanuvchi_olish),
    db: AsyncSession = Depends(sessiya_olish)
):
    """Ma'lum savolga o'tish."""
    servis = ImtihonServisi(db)
    savol = await servis.savolga_otish(
        imtihon_id, joriy_foydalanuvchi.id, savol_indeksi
    )
    
    if not savol:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Savolga o'tib bo'lmadi"
        )
    
    await db.commit()
    return ImtihonSavoli(**savol)


@router.post(
    "/{imtihon_id}/yakunlash",
    response_model=ImtihonNatijasi,
    summary="Imtihonni yakunlash"
)
async def imtihon_yakunlash(
    imtihon_id: UUID,
    joriy_foydalanuvchi: Foydalanuvchi = Depends(joriy_foydalanuvchi_olish),
    db: AsyncSession = Depends(sessiya_olish)
):
    """Imtihonni yakunlash va natijani olish."""
    servis = ImtihonServisi(db)
    
    try:
        imtihon = await servis.yakunlash(imtihon_id, joriy_foydalanuvchi.id)
        await db.commit()
        
        # To'liq ma'lumot olish
        imtihon = await servis.olish(imtihon_id, joriy_foydalanuvchi.id)
        return imtihon_natijasiga(imtihon, javoblar_bilan=True)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "/{imtihon_id}/natija",
    response_model=ImtihonNatijasi,
    summary="Imtihon natijasi"
)
async def imtihon_natijasi(
    imtihon_id: UUID,
    joriy_foydalanuvchi: Foydalanuvchi = Depends(joriy_foydalanuvchi_olish),
    db: AsyncSession = Depends(sessiya_olish)
):
    """Yakunlangan imtihon natijasi."""
    servis = ImtihonServisi(db)
    imtihon = await servis.olish(imtihon_id, joriy_foydalanuvchi.id)
    
    if not imtihon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Imtihon topilmadi"
        )
    
    if imtihon.holat != ImtihonHolati.TUGALLANGAN:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Imtihon hali yakunlanmagan"
        )
    
    return imtihon_natijasiga(imtihon, javoblar_bilan=True)


# ============== Ro'yxat va statistika ==============

@router.get(
    "/",
    response_model=ImtihonlarRoyxati,
    summary="Mening imtihonlarim"
)
async def mening_imtihonlarim(
    sahifa: int = Query(1, ge=1),
    hajm: int = Query(20, ge=1, le=100),
    joriy_foydalanuvchi: Foydalanuvchi = Depends(joriy_foydalanuvchi_olish),
    db: AsyncSession = Depends(sessiya_olish)
):
    """Foydalanuvchi imtihonlari ro'yxati."""
    servis = ImtihonServisi(db)
    imtihonlar, jami = await servis.foydalanuvchi_imtihonlari(
        joriy_foydalanuvchi.id, sahifa, hajm
    )
    
    sahifalar_soni = (jami + hajm - 1) // hajm if hajm > 0 else 0
    
    return ImtihonlarRoyxati(
        imtihonlar=[imtihon_natijasiga(i) for i in imtihonlar],
        jami=jami,
        sahifa=sahifa,
        hajm=hajm,
        sahifalar_soni=sahifalar_soni
    )


@router.get(
    "/statistika/mening",
    response_model=ImtihonStatistikasi,
    summary="Imtihon statistikasi"
)
async def imtihon_statistikasi(
    joriy_foydalanuvchi: Foydalanuvchi = Depends(joriy_foydalanuvchi_olish),
    db: AsyncSession = Depends(sessiya_olish)
):
    """Foydalanuvchi imtihon statistikasi."""
    servis = ImtihonServisi(db)
    stat = await servis.statistika(joriy_foydalanuvchi.id)
    return ImtihonStatistikasi(**stat)


@router.delete(
    "/{imtihon_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Imtihonni bekor qilish"
)
async def imtihon_bekor_qilish(
    imtihon_id: UUID,
    joriy_foydalanuvchi: Foydalanuvchi = Depends(joriy_foydalanuvchi_olish),
    db: AsyncSession = Depends(sessiya_olish)
):
    """Jarayondagi imtihonni bekor qilish."""
    servis = ImtihonServisi(db)
    imtihon = await servis.olish(imtihon_id, joriy_foydalanuvchi.id)
    
    if not imtihon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Imtihon topilmadi"
        )
    
    if imtihon.holat == ImtihonHolati.TUGALLANGAN:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Yakunlangan imtihonni bekor qilib bo'lmaydi"
        )
    
    from modellar.imtihon import ImtihonHolati as IH
    imtihon.holat = IH.BEKOR_QILINGAN
    await db.commit()
