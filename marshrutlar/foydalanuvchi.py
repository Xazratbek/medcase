# MedCase Platform - Foydalanuvchi Marshrutlari
# Profil boshqaruvi

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from sozlamalar.malumotlar_bazasi import sessiya_olish
from servislar.foydalanuvchi_servisi import FoydalanuvchiServisi
from servislar.media_servisi import media_servisi
from sxemalar.foydalanuvchi import (
    FoydalanuvchiJavob,
    FoydalanuvchiYangilash,
    FoydalanuvchiToliqJavob,
    ProfilYangilash,
    ProfilJavob
)
from sxemalar.asosiy import MuvaffaqiyatJavob
from middleware.autentifikatsiya import joriy_foydalanuvchi_olish
from modellar.foydalanuvchi import Foydalanuvchi

router = APIRouter()


@router.post(
    "/profil/avatar",
    summary="Avatar rasmini yuklash"
)
async def avatar_yuklash(
    rasm: UploadFile = File(...),
    joriy_foydalanuvchi: Foydalanuvchi = Depends(joriy_foydalanuvchi_olish),
    db: AsyncSession = Depends(sessiya_olish)
):
    """
    Foydalanuvchi avatar rasmini Cloudinary ga yuklaydi.
    """
    # Fayl turini tekshirish
    if not rasm.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Faqat rasm fayllari qabul qilinadi"
        )

    # Fayl hajmini tekshirish (5MB maksimum)
    mazmun = await rasm.read()
    if len(mazmun) > 5 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Rasm hajmi 5MB dan oshmasligi kerak"
        )

    # Fayl pozitsiyasini qaytarish
    await rasm.seek(0)

    # Cloudinary ga yuklash
    natija = await media_servisi.rasm_yuklash(
        rasm,
        jild=f"medcase/avatars/{joriy_foydalanuvchi.id}"
    )

    if not natija.get("muvaffaqiyat"):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=natija.get("xato", "Rasm yuklashda xatolik")
        )

    # Profilda avatar URL ni yangilash
    servis = FoydalanuvchiServisi(db)

    # Eager load with retry pattern to fix MissingGreenlet
    try:
        # Check if profile is loaded
        _ = joriy_foydalanuvchi.profil
    except Exception:
        # Reload user with profile if accessing it fails
        from sqlalchemy import select
        from sqlalchemy.orm import selectinload

        reloaded_user = await db.execute(
            select(Foydalanuvchi)
            .where(Foydalanuvchi.id == joriy_foydalanuvchi.id)
            .options(selectinload(Foydalanuvchi.profil))
        )
        joriy_foydalanuvchi = reloaded_user.scalar_one()

    # Profilni olish yoki yaratish
    if not joriy_foydalanuvchi.profil:
        await servis.profil_yaratish(joriy_foydalanuvchi.id)

    # Avatar URL ni yangilash
    profil = await servis.profil_yangilash(
        joriy_foydalanuvchi.id,
        ProfilYangilash(avatar_url=natija["url"])
    )

    return {
        "muvaffaqiyat": True,
        "malumot": {
            "avatar_url": natija["url"]
        },
        "xabar": "Avatar muvaffaqiyatli yuklandi"
    }


@router.get(
    "/profil",
    response_model=FoydalanuvchiToliqJavob,
    summary="Joriy foydalanuvchi profili"
)
async def profil_olish(
    joriy_foydalanuvchi: Foydalanuvchi = Depends(joriy_foydalanuvchi_olish),
    db: AsyncSession = Depends(sessiya_olish)
):
    """
    Joriy foydalanuvchining to'liq profil ma'lumotlarini qaytaradi.
    """
    servis = FoydalanuvchiServisi(db)
    foydalanuvchi = await servis.toliq_olish(joriy_foydalanuvchi.id)
    return foydalanuvchi


@router.put(
    "/profil",
    response_model=FoydalanuvchiJavob,
    summary="Foydalanuvchi ma'lumotlarini yangilash"
)
async def foydalanuvchi_yangilash(
    malumot: FoydalanuvchiYangilash,
    joriy_foydalanuvchi: Foydalanuvchi = Depends(joriy_foydalanuvchi_olish),
    db: AsyncSession = Depends(sessiya_olish)
):
    """
    Foydalanuvchi asosiy ma'lumotlarini yangilaydi.
    """
    servis = FoydalanuvchiServisi(db)

    # Foydalanuvchi nomi tekshirish
    if malumot.foydalanuvchi_nomi:
        mavjud = await servis.nom_bilan_olish(malumot.foydalanuvchi_nomi)
        if mavjud and mavjud.id != joriy_foydalanuvchi.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Bu foydalanuvchi nomi band"
            )

    foydalanuvchi = await servis.yangilash(
        joriy_foydalanuvchi.id,
        **malumot.model_dump(exclude_unset=True)
    )
    return foydalanuvchi


@router.put(
    "/profil/qoshimcha",
    response_model=ProfilJavob,
    summary="Qo'shimcha profil ma'lumotlarini yangilash"
)
async def profil_qoshimcha_yangilash(
    malumot: ProfilYangilash,
    joriy_foydalanuvchi: Foydalanuvchi = Depends(joriy_foydalanuvchi_olish),
    db: AsyncSession = Depends(sessiya_olish)
):
    """
    Foydalanuvchi qo'shimcha profil ma'lumotlarini yangilaydi.
    """
    servis = FoydalanuvchiServisi(db)
    profil = await servis.profil_yangilash(joriy_foydalanuvchi.id, malumot)

    if not profil:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profil topilmadi"
        )

    return profil


@router.get(
    "/{foydalanuvchi_id}",
    response_model=FoydalanuvchiJavob,
    summary="Foydalanuvchi ma'lumotlarini ko'rish"
)
async def foydalanuvchi_olish(
    foydalanuvchi_id: UUID,
    db: AsyncSession = Depends(sessiya_olish)
):
    """
    Boshqa foydalanuvchi ommaviy ma'lumotlarini ko'rish.
    """
    servis = FoydalanuvchiServisi(db)
    foydalanuvchi = await servis.toliq_olish(foydalanuvchi_id)

    if not foydalanuvchi:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Foydalanuvchi topilmadi"
        )

    # Profil yopiq bo'lsa
    if foydalanuvchi.profil and not foydalanuvchi.profil.profil_ochiq:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bu profil yopiq"
        )

    return foydalanuvchi


@router.delete(
    "/profil",
    response_model=MuvaffaqiyatJavob,
    summary="Hisobni o'chirish"
)
async def hisob_ochirish(
    joriy_foydalanuvchi: Foydalanuvchi = Depends(joriy_foydalanuvchi_olish),
    db: AsyncSession = Depends(sessiya_olish)
):
    """
    Foydalanuvchi hisobini o'chiradi (yumshoq o'chirish).
    """
    servis = FoydalanuvchiServisi(db)
    await servis.ochirish(joriy_foydalanuvchi.id, yumshoq=True)

    return MuvaffaqiyatJavob(xabar="Hisob muvaffaqiyatli o'chirildi")


@router.get(
    "/sessiyalar",
    summary="Faol sessiyalar ro'yxati"
)
async def sessiyalar_royxati(
    joriy_foydalanuvchi: Foydalanuvchi = Depends(joriy_foydalanuvchi_olish),
    db: AsyncSession = Depends(sessiya_olish)
):
    """
    Foydalanuvchining barcha faol sessiyalarini qaytaradi.
    """
    from servislar.autentifikatsiya_servisi import AutentifikatsiyaServisi

    auth_servis = AutentifikatsiyaServisi(db)
    sessiyalar = await auth_servis.sessiyalar_olish(joriy_foydalanuvchi.id)

    return {
        "sessiyalar": [
            {
                "id": str(s.id),
                "qurilma_turi": s.qurilma_turi,
                "qurilma_nomi": s.qurilma_nomi,
                "brauzer": s.brauzer,
                "ip_manzil": s.ip_manzil,
                "oxirgi_faollik": s.oxirgi_faollik,
                "yaratilgan_vaqt": s.yaratilgan_vaqt
            }
            for s in sessiyalar
        ]
    }
