# MedCase Platform - Export Marshrutlari
# PDF va Excel hisobotlar

from fastapi import APIRouter, Depends, Query, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
from typing import Optional
import io

from sozlamalar.malumotlar_bazasi import sessiya_olish
from servislar.export_servisi import ExportServisi
from middleware.autentifikatsiya import joriy_foydalanuvchi_olish
from modellar.foydalanuvchi import Foydalanuvchi

router = APIRouter()


@router.get("/rivojlanish/pdf", summary="Rivojlanish hisoboti (PDF)")
async def rivojlanish_pdf(
    boshlangich_sana: Optional[datetime] = None,
    tugash_sana: Optional[datetime] = None,
    joriy_foydalanuvchi: Foydalanuvchi = Depends(joriy_foydalanuvchi_olish),
    db: AsyncSession = Depends(sessiya_olish)
):
    """Foydalanuvchi rivojlanish hisobotini PDF formatda yuklab olish."""
    servis = ExportServisi(db)
    
    try:
        pdf_bytes = await servis.rivojlanish_pdf(
            joriy_foydalanuvchi.id,
            boshlangich_sana,
            tugash_sana
        )
        
        fayl_nomi = f"rivojlanish_hisoboti_{datetime.now().strftime('%Y%m%d')}.pdf"
        
        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={fayl_nomi}"
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"PDF yaratishda xatolik: {str(e)}"
        )


@router.get("/rivojlanish/excel", summary="Rivojlanish hisoboti (Excel)")
async def rivojlanish_excel(
    boshlangich_sana: Optional[datetime] = None,
    tugash_sana: Optional[datetime] = None,
    joriy_foydalanuvchi: Foydalanuvchi = Depends(joriy_foydalanuvchi_olish),
    db: AsyncSession = Depends(sessiya_olish)
):
    """Foydalanuvchi rivojlanish hisobotini Excel formatda yuklab olish."""
    servis = ExportServisi(db)
    
    try:
        excel_bytes = await servis.rivojlanish_excel(
            joriy_foydalanuvchi.id,
            boshlangich_sana,
            tugash_sana
        )
        
        fayl_nomi = f"rivojlanish_hisoboti_{datetime.now().strftime('%Y%m%d')}.xlsx"
        
        return StreamingResponse(
            io.BytesIO(excel_bytes),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": f"attachment; filename={fayl_nomi}"
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Excel yaratishda xatolik: {str(e)}"
        )
