# MedCase Platform - Bildirishnoma Marshrutlari

from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel

from sozlamalar.malumotlar_bazasi import sessiya_olish
from servislar.bildirishnoma_servisi import BildirishnomServisi
from sxemalar.asosiy import MuvaffaqiyatJavob
from middleware.autentifikatsiya import joriy_foydalanuvchi_olish
from modellar.foydalanuvchi import Foydalanuvchi

router = APIRouter()


# ============== Sxemalar ==============

class BildirishnomaSozlamalarYangilash(BaseModel):
    """Bildirishnoma sozlamalarini yangilash sxemasi."""
    # Email bildirshnomalari
    email_yutuqlar: Optional[bool] = None
    email_streak: Optional[bool] = None
    email_yangi_kontent: Optional[bool] = None
    email_haftalik_hisobot: Optional[bool] = None
    
    # Push bildirshnomalari
    push_yutuqlar: Optional[bool] = None
    push_streak: Optional[bool] = None
    push_eslatma: Optional[bool] = None
    push_reyting: Optional[bool] = None
    
    # Ilova ichidagi bildirishnomalar
    ilova_yutuqlar: Optional[bool] = None
    ilova_streak: Optional[bool] = None
    ilova_yangi_kontent: Optional[bool] = None
    ilova_tizim: Optional[bool] = None
    
    # Sokin rejim
    sokin_rejim: Optional[bool] = None
    sokin_boshlanish: Optional[str] = None
    sokin_tugash: Optional[str] = None


class EslatmaVaqtlari(BaseModel):
    """Eslatma vaqtlari."""
    soat: int = 9
    daqiqa: int = 0
    kunlar: List[int] = [1, 2, 3, 4, 5]  # 1=Dush, 7=Yak


@router.get("/", summary="Bildirishnomalar ro'yxati")
async def bildirishnomalar_royxati(
    oqilmagan_faqat: bool = False,
    sahifa: int = Query(1, ge=1),
    hajm: int = Query(20, ge=1, le=100),
    joriy_foydalanuvchi: Foydalanuvchi = Depends(joriy_foydalanuvchi_olish),
    db: AsyncSession = Depends(sessiya_olish)
):
    """Foydalanuvchi bildirishnomalarini qaytaradi."""
    servis = BildirishnomServisi(db)
    bildirishnomalar, jami = await servis.royxat_olish(
        joriy_foydalanuvchi.id, oqilmagan_faqat, sahifa, hajm
    )
    oqilmagan_soni = await servis.oqilmagan_soni(joriy_foydalanuvchi.id)
    
    return {
        "bildirishnomalar": bildirishnomalar,
        "jami": jami,
        "oqilmagan_soni": oqilmagan_soni,
        "sahifa": sahifa,
        "hajm": hajm
    }


@router.get("/oqilmagan-soni", summary="O'qilmagan soni")
async def oqilmagan_soni(
    joriy_foydalanuvchi: Foydalanuvchi = Depends(joriy_foydalanuvchi_olish),
    db: AsyncSession = Depends(sessiya_olish)
):
    """O'qilmagan bildirishnomalar sonini qaytaradi."""
    servis = BildirishnomServisi(db)
    soni = await servis.oqilmagan_soni(joriy_foydalanuvchi.id)
    return {"oqilmagan_soni": soni}


@router.post("/{bildirishnoma_id}/oqilgan", response_model=MuvaffaqiyatJavob)
async def oqilgan_belgilash(
    bildirishnoma_id: UUID,
    joriy_foydalanuvchi: Foydalanuvchi = Depends(joriy_foydalanuvchi_olish),
    db: AsyncSession = Depends(sessiya_olish)
):
    """Bildirishnomani o'qilgan deb belgilaydi."""
    servis = BildirishnomServisi(db)
    await servis.oqilgan_belgilash(bildirishnoma_id, joriy_foydalanuvchi.id)
    return MuvaffaqiyatJavob(xabar="Bildirishnoma o'qilgan deb belgilandi")


@router.post("/hammasi-oqilgan", response_model=MuvaffaqiyatJavob)
async def hammasi_oqilgan(
    joriy_foydalanuvchi: Foydalanuvchi = Depends(joriy_foydalanuvchi_olish),
    db: AsyncSession = Depends(sessiya_olish)
):
    """Barcha bildirishnomalarni o'qilgan deb belgilaydi."""
    servis = BildirishnomServisi(db)
    soni = await servis.hammasini_oqilgan_belgilash(joriy_foydalanuvchi.id)
    return MuvaffaqiyatJavob(xabar=f"{soni} ta bildirishnoma o'qilgan deb belgilandi")


# ============== Sozlamalar ==============

@router.get("/sozlamalar", summary="Bildirishnoma sozlamalarini olish")
async def sozlamalar_olish(
    joriy_foydalanuvchi: Foydalanuvchi = Depends(joriy_foydalanuvchi_olish),
    db: AsyncSession = Depends(sessiya_olish)
):
    """Foydalanuvchi bildirishnoma sozlamalarini qaytaradi."""
    servis = BildirishnomServisi(db)
    sozlamalar = await servis.sozlamalar_olish(joriy_foydalanuvchi.id)
    
    if not sozlamalar:
        # Default sozlamalar yaratish
        sozlamalar = await servis.sozlamalar_yangilash(joriy_foydalanuvchi.id)
    
    return {
        "email_yutuqlar": sozlamalar.email_yutuqlar,
        "email_streak": sozlamalar.email_streak,
        "email_yangi_kontent": sozlamalar.email_yangi_kontent,
        "email_haftalik_hisobot": sozlamalar.email_haftalik_hisobot,
        "push_yutuqlar": sozlamalar.push_yutuqlar,
        "push_streak": sozlamalar.push_streak,
        "push_eslatma": sozlamalar.push_eslatma,
        "push_reyting": sozlamalar.push_reyting,
        "ilova_yutuqlar": sozlamalar.ilova_yutuqlar,
        "ilova_streak": sozlamalar.ilova_streak,
        "ilova_yangi_kontent": sozlamalar.ilova_yangi_kontent,
        "ilova_tizim": sozlamalar.ilova_tizim,
        "eslatma_vaqtlari": sozlamalar.eslatma_vaqtlari,
        "sokin_rejim": sozlamalar.sokin_rejim,
        "sokin_boshlanish": sozlamalar.sokin_boshlanish,
        "sokin_tugash": sozlamalar.sokin_tugash
    }


@router.put("/sozlamalar", summary="Bildirishnoma sozlamalarini yangilash")
async def sozlamalar_yangilash(
    malumot: BildirishnomaSozlamalarYangilash,
    joriy_foydalanuvchi: Foydalanuvchi = Depends(joriy_foydalanuvchi_olish),
    db: AsyncSession = Depends(sessiya_olish)
):
    """Foydalanuvchi bildirishnoma sozlamalarini yangilaydi."""
    servis = BildirishnomServisi(db)
    
    # Faqat berilgan qiymatlarni yangilash
    yangilash_malumotlari = malumot.model_dump(exclude_unset=True)
    
    if not yangilash_malumotlari:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Yangilash uchun ma'lumot berilmadi"
        )
    
    sozlamalar = await servis.sozlamalar_yangilash(
        joriy_foydalanuvchi.id,
        **yangilash_malumotlari
    )
    
    return {
        "xabar": "Sozlamalar yangilandi",
        "malumot": {
            "email_yutuqlar": sozlamalar.email_yutuqlar,
            "email_streak": sozlamalar.email_streak,
            "email_yangi_kontent": sozlamalar.email_yangi_kontent,
            "email_haftalik_hisobot": sozlamalar.email_haftalik_hisobot,
            "push_yutuqlar": sozlamalar.push_yutuqlar,
            "push_streak": sozlamalar.push_streak,
            "push_eslatma": sozlamalar.push_eslatma,
            "push_reyting": sozlamalar.push_reyting,
            "ilova_yutuqlar": sozlamalar.ilova_yutuqlar,
            "ilova_streak": sozlamalar.ilova_streak,
            "ilova_yangi_kontent": sozlamalar.ilova_yangi_kontent,
            "ilova_tizim": sozlamalar.ilova_tizim,
            "sokin_rejim": sozlamalar.sokin_rejim,
            "sokin_boshlanish": sozlamalar.sokin_boshlanish,
            "sokin_tugash": sozlamalar.sokin_tugash
        }
    }


@router.put("/sozlamalar/eslatma-vaqtlari", summary="Eslatma vaqtlarini yangilash")
async def eslatma_vaqtlari_yangilash(
    malumot: EslatmaVaqtlari,
    joriy_foydalanuvchi: Foydalanuvchi = Depends(joriy_foydalanuvchi_olish),
    db: AsyncSession = Depends(sessiya_olish)
):
    """Eslatma vaqtlarini yangilaydi."""
    servis = BildirishnomServisi(db)
    
    eslatma_vaqtlari = {
        "soat": malumot.soat,
        "daqiqa": malumot.daqiqa,
        "kunlar": malumot.kunlar
    }
    
    sozlamalar = await servis.sozlamalar_yangilash(
        joriy_foydalanuvchi.id,
        eslatma_vaqtlari=eslatma_vaqtlari
    )
    
    return {
        "xabar": "Eslatma vaqtlari yangilandi",
        "eslatma_vaqtlari": sozlamalar.eslatma_vaqtlari
    }
