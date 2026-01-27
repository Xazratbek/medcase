# MedCase Platform - Autentifikatsiya Middleware
# JWT token tekshirish va foydalanuvchi olish

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from uuid import UUID

from sozlamalar.malumotlar_bazasi import sessiya_olish
from yordamchilar.xavfsizlik import token_dekodlash
from modellar.foydalanuvchi import Foydalanuvchi, FoydalanuvchiRoli

xavfsizlik = HTTPBearer(auto_error=False)


async def joriy_foydalanuvchi_olish(
    credentials: HTTPAuthorizationCredentials = Depends(xavfsizlik),
    db: AsyncSession = Depends(sessiya_olish)
) -> Foydalanuvchi:
    """
    JWT tokendan joriy foydalanuvchini oladi.
    Token yo'q yoki yaroqsiz bo'lsa, 401 xatosi qaytaradi.
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Autentifikatsiya talab qilinadi",
            headers={"WWW-Authenticate": "Bearer"}
        )

    token = credentials.credentials
    payload = token_dekodlash(token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token yaroqsiz yoki muddati o'tgan",
            headers={"WWW-Authenticate": "Bearer"}
        )

    foydalanuvchi_id = payload.get("foydalanuvchi_id")
    if not foydalanuvchi_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token yaroqsiz"
        )

    # Foydalanuvchini bazadan olish
    from sqlalchemy import select
    from sqlalchemy.orm import selectinload

    sorov = (
        select(Foydalanuvchi)
        .where(Foydalanuvchi.id == UUID(foydalanuvchi_id))
        .options(
            selectinload(Foydalanuvchi.profil),
            selectinload(Foydalanuvchi.rivojlanish)
        )
    )
    natija = await db.execute(sorov)
    foydalanuvchi = natija.scalar_one_or_none()

    if not foydalanuvchi:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Foydalanuvchi topilmadi"
        )

    if not foydalanuvchi.faol:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Hisob faol emas"
        )

    return foydalanuvchi


async def ixtiyoriy_foydalanuvchi(
    credentials: HTTPAuthorizationCredentials = Depends(xavfsizlik),
    db: AsyncSession = Depends(sessiya_olish)
) -> Optional[Foydalanuvchi]:
    """
    Ixtiyoriy autentifikatsiya - token bo'lmasa None qaytaradi.
    """
    if not credentials:
        return None

    try:
        return await joriy_foydalanuvchi_olish(credentials, db)
    except HTTPException:
        return None


async def admin_talab_qilish(
    joriy_foydalanuvchi: Foydalanuvchi = Depends(joriy_foydalanuvchi_olish)
) -> Foydalanuvchi:
    """
    Admin huquqini tekshiradi.
    """
    if joriy_foydalanuvchi.rol not in [
        FoydalanuvchiRoli.ADMIN,
        FoydalanuvchiRoli.SUPER_ADMIN
    ]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin huquqi talab qilinadi"
        )
    return joriy_foydalanuvchi


async def oqituvchi_talab_qilish(
    joriy_foydalanuvchi: Foydalanuvchi = Depends(joriy_foydalanuvchi_olish)
) -> Foydalanuvchi:
    """
    O'qituvchi yoki admin huquqini tekshiradi.
    """
    if joriy_foydalanuvchi.rol not in [
        FoydalanuvchiRoli.OQITUVCHI,
        FoydalanuvchiRoli.ADMIN,
        FoydalanuvchiRoli.SUPER_ADMIN
    ]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="O'qituvchi huquqi talab qilinadi"
        )
    return joriy_foydalanuvchi
