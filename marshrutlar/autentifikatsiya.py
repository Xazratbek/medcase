# MedCase Platform - Autentifikatsiya Marshrutlari
# Kirish, chiqish, ro'yxatdan o'tish
# OPTIMIZED: Single query for uniqueness check, parallel operations

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession

from sozlamalar.malumotlar_bazasi import sessiya_olish
from servislar.foydalanuvchi_servisi import FoydalanuvchiServisi
from servislar.autentifikatsiya_servisi import AutentifikatsiyaServisi
from sxemalar.foydalanuvchi import (
    FoydalanuvchiYaratish,
    FoydalanuvchiKirish,
    FoydalanuvchiJavob,
    TokenJavob,
    TokenYangilash,
    ParolOzgartirish,
    ParolTiklash
)
from sxemalar.asosiy import MuvaffaqiyatJavob, XatoJavob
from middleware.autentifikatsiya import joriy_foydalanuvchi_olish
from modellar.foydalanuvchi import Foydalanuvchi

router = APIRouter()


@router.post(
    "/royxatdan-otish",
    response_model=FoydalanuvchiJavob,
    status_code=status.HTTP_201_CREATED,
    summary="Yangi foydalanuvchi ro'yxatdan o'tkazish"
)
async def royxatdan_otish(
    malumot: FoydalanuvchiYaratish,
    db: AsyncSession = Depends(sessiya_olish)
):
    """
    Yangi foydalanuvchi ro'yxatdan o'tkazadi.
    OPTIMIZED: Single DB query for email+nom check
    
    - **email**: Unikal email manzil
    - **foydalanuvchi_nomi**: Unikal foydalanuvchi nomi
    - **parol**: Kamida 8 ta belgi, katta va kichik harf, raqam
    - **ism**: Foydalanuvchi ismi
    - **familiya**: Foydalanuvchi familiyasi
    """
    servis = FoydalanuvchiServisi(db)
    
    # BITTA so'rov bilan email va nom tekshirish
    email_mavjud, nom_mavjud = await servis.email_va_nom_mavjud(
        malumot.email, 
        malumot.foydalanuvchi_nomi
    )
    
    if email_mavjud:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bu email allaqachon ro'yxatdan o'tgan"
        )
    
    if nom_mavjud:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bu foydalanuvchi nomi band"
        )
    
    foydalanuvchi = await servis.yaratish_toliq(malumot)
    return foydalanuvchi


@router.post(
    "/kirish",
    response_model=TokenJavob,
    summary="Tizimga kirish"
)
async def kirish(
    malumot: FoydalanuvchiKirish,
    request: Request,
    db: AsyncSession = Depends(sessiya_olish)
):
    """
    Tizimga kirish va token olish.
    
    - **email_yoki_nom**: Email yoki foydalanuvchi nomi
    - **parol**: Parol
    """
    foyd_servis = FoydalanuvchiServisi(db)
    auth_servis = AutentifikatsiyaServisi(db)
    
    # Foydalanuvchini topish
    foydalanuvchi = await foyd_servis.email_yoki_nom_bilan_olish(
        malumot.email_yoki_nom
    )
    
    if not foydalanuvchi:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email/nom yoki parol noto'g'ri"
        )
    
    # Faollik tekshirish
    if not foydalanuvchi.faol:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Hisob faol emas"
        )
    
    # Parol tekshirish
    if not await foyd_servis.parol_tekshirish(foydalanuvchi, malumot.parol):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email/nom yoki parol noto'g'ri"
        )
    
    # Qurilma ma'lumotlari
    qurilma_malumoti = {
        "ip_manzil": request.client.host if request.client else None,
        "qurilma_turi": request.headers.get("X-Device-Type"),
        "brauzer": request.headers.get("User-Agent")
    }
    
    token = await auth_servis.kirish(foydalanuvchi, qurilma_malumoti)
    return token


@router.post(
    "/token-yangilash",
    response_model=TokenJavob,
    summary="Tokenni yangilash"
)
async def token_yangilash(
    malumot: TokenYangilash,
    db: AsyncSession = Depends(sessiya_olish)
):
    """
    Yangilash tokeni yordamida yangi tokenlar olish.
    """
    auth_servis = AutentifikatsiyaServisi(db)
    
    token = await auth_servis.token_yangilash(malumot.yangilash_tokeni)
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Yangilash tokeni yaroqsiz yoki muddati o'tgan"
        )
    
    return token


@router.post(
    "/chiqish",
    response_model=MuvaffaqiyatJavob,
    summary="Tizimdan chiqish"
)
async def chiqish(
    malumot: TokenYangilash = None,
    hammasi: bool = False,
    joriy_foydalanuvchi: Foydalanuvchi = Depends(joriy_foydalanuvchi_olish),
    db: AsyncSession = Depends(sessiya_olish)
):
    """
    Tizimdan chiqish.
    
    - **hammasi**: True bo'lsa, barcha qurilmalardan chiqadi
    """
    auth_servis = AutentifikatsiyaServisi(db)
    
    await auth_servis.chiqish(
        joriy_foydalanuvchi.id,
        yangilash_tokeni=malumot.yangilash_tokeni if malumot else None,
        hammasi=hammasi
    )
    
    return MuvaffaqiyatJavob(xabar="Muvaffaqiyatli chiqildi")


@router.post(
    "/parol-ozgartirish",
    response_model=MuvaffaqiyatJavob,
    summary="Parolni o'zgartirish"
)
async def parol_ozgartirish(
    malumot: ParolOzgartirish,
    joriy_foydalanuvchi: Foydalanuvchi = Depends(joriy_foydalanuvchi_olish),
    db: AsyncSession = Depends(sessiya_olish)
):
    """
    Joriy parolni yangi parolga o'zgartirish.
    """
    foyd_servis = FoydalanuvchiServisi(db)
    
    # Joriy parolni tekshirish
    if not await foyd_servis.parol_tekshirish(
        joriy_foydalanuvchi,
        malumot.joriy_parol
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Joriy parol noto'g'ri"
        )
    
    await foyd_servis.parol_yangilash(
        joriy_foydalanuvchi.id,
        malumot.yangi_parol
    )
    
    return MuvaffaqiyatJavob(xabar="Parol muvaffaqiyatli o'zgartirildi")


@router.get(
    "/men",
    response_model=FoydalanuvchiJavob,
    summary="Joriy foydalanuvchi ma'lumotlari"
)
async def joriy_foydalanuvchi_malumotlari(
    joriy_foydalanuvchi: Foydalanuvchi = Depends(joriy_foydalanuvchi_olish)
):
    """
    Joriy autentifikatsiya qilingan foydalanuvchi ma'lumotlarini qaytaradi.
    """
    return joriy_foydalanuvchi
