# MedCase Platform - Qidiruv Marshrutlari
# Full-text search API

from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from uuid import UUID

from sozlamalar.malumotlar_bazasi import sessiya_olish
from servislar.qidiruv_servisi import QidiruvServisi
from middleware.autentifikatsiya import ixtiyoriy_foydalanuvchi
from modellar.foydalanuvchi import Foydalanuvchi

router = APIRouter()


@router.get("/", summary="Umumiy qidiruv")
async def umumiy_qidiruv(
    q: str = Query(..., min_length=2, max_length=100, description="Qidiruv so'zi"),
    db: AsyncSession = Depends(sessiya_olish)
):
    """
    Barcha turlar bo'yicha umumiy qidiruv.
    Holatlar, kategoriyalar va foydalanuvchilarni qaytaradi.
    """
    servis = QidiruvServisi(db)
    natija = await servis.umumiy_qidiruv(q)
    return natija


@router.get("/holatlar", summary="Holatlarni qidirish")
async def holatlar_qidirish(
    q: str = Query(..., min_length=2, max_length=100),
    kategoriya_id: Optional[UUID] = None,
    qiyinlik: Optional[str] = None,
    sahifa: int = Query(1, ge=1),
    hajm: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(sessiya_olish)
):
    """Holatlarni full-text search bilan qidiradi."""
    servis = QidiruvServisi(db)
    holatlar, jami = await servis.holatlar_qidirish(
        q,
        kategoriya_id=kategoriya_id,
        qiyinlik=qiyinlik,
        sahifa=sahifa,
        hajm=hajm
    )
    
    return {
        "natijalar": holatlar,
        "jami": jami,
        "sahifa": sahifa,
        "hajm": hajm,
        "sahifalar_soni": (jami + hajm - 1) // hajm if jami > 0 else 0
    }


@router.get("/kategoriyalar", summary="Kategoriyalarni qidirish")
async def kategoriyalar_qidirish(
    q: str = Query(..., min_length=2, max_length=100),
    sahifa: int = Query(1, ge=1),
    hajm: int = Query(20, ge=1, le=50),
    db: AsyncSession = Depends(sessiya_olish)
):
    """Kategoriyalarni qidiradi."""
    servis = QidiruvServisi(db)
    kategoriyalar, jami = await servis.kategoriyalar_qidirish(q, sahifa, hajm)
    
    return {
        "natijalar": kategoriyalar,
        "jami": jami,
        "sahifa": sahifa,
        "hajm": hajm
    }


@router.get("/foydalanuvchilar", summary="Foydalanuvchilarni qidirish")
async def foydalanuvchilar_qidirish(
    q: str = Query(..., min_length=2, max_length=100),
    sahifa: int = Query(1, ge=1),
    hajm: int = Query(20, ge=1, le=50),
    db: AsyncSession = Depends(sessiya_olish)
):
    """Foydalanuvchilarni qidiradi (faqat profili ochiq bo'lganlar)."""
    servis = QidiruvServisi(db)
    foydalanuvchilar, jami = await servis.foydalanuvchilar_qidirish(q, sahifa, hajm)
    
    return {
        "natijalar": foydalanuvchilar,
        "jami": jami,
        "sahifa": sahifa,
        "hajm": hajm
    }


@router.get("/taklif", summary="Autocomplete taklif")
async def taklif_qidiruv(
    q: str = Query(..., min_length=1, max_length=50),
    limit: int = Query(10, ge=1, le=20),
    db: AsyncSession = Depends(sessiya_olish)
):
    """
    Autocomplete uchun tez taklif qidiruv.
    Foydalanuvchi yozayotganda real-time taklif beradi.
    """
    servis = QidiruvServisi(db)
    takliflar = await servis.taklif_qidiruv(q, limit)
    
    return {"takliflar": takliflar}
