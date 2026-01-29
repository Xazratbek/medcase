# MedCase Platform - Admin Marshrutlari
# Kontent va foydalanuvchi boshqaruvi

from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File, Body
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any
from uuid import UUID

from sozlamalar.malumotlar_bazasi import sessiya_olish
from servislar.foydalanuvchi_servisi import FoydalanuvchiServisi
from servislar.kategoriya_servisi import KategoriyaServisi
from servislar.holat_servisi import HolatServisi
from servislar.media_servisi import media_servisi
from servislar.import_servisi import ImportServisi
from sxemalar.kategoriya import (
    AsosiyKategoriyaYaratish, AsosiyKategoriyaYangilash,
    KichikKategoriyaYaratish, BolimYaratish
)
from sxemalar.holat import HolatYaratish, HolatYangilash
from sxemalar.asosiy import MuvaffaqiyatJavob
from middleware.autentifikatsiya import admin_talab_qilish
from modellar.foydalanuvchi import Foydalanuvchi, FoydalanuvchiRoli

router = APIRouter()


# ============== Kategoriya boshqaruvi ==============

@router.post("/kategoriya/asosiy", summary="Asosiy kategoriya yaratish")
async def asosiy_kategoriya_yaratish(
    malumot: AsosiyKategoriyaYaratish,
    admin: Foydalanuvchi = Depends(admin_talab_qilish),
    db: AsyncSession = Depends(sessiya_olish)
):
    """Yangi asosiy kategoriya yaratadi."""
    servis = KategoriyaServisi(db)
    kategoriya = await servis.asosiy_kategoriya_yaratish(malumot)
    return kategoriya


@router.post("/kategoriya/kichik", summary="Kichik kategoriya yaratish")
async def kichik_kategoriya_yaratish(
    malumot: KichikKategoriyaYaratish,
    admin: Foydalanuvchi = Depends(admin_talab_qilish),
    db: AsyncSession = Depends(sessiya_olish)
):
    """Yangi kichik kategoriya yaratadi."""
    servis = KategoriyaServisi(db)
    kategoriya = await servis.kichik_kategoriya_yaratish(malumot)
    return kategoriya


@router.post("/kategoriya/bolim", summary="Bo'lim yaratish")
async def bolim_yaratish(
    malumot: BolimYaratish,
    admin: Foydalanuvchi = Depends(admin_talab_qilish),
    db: AsyncSession = Depends(sessiya_olish)
):
    """Yangi bo'lim yaratadi."""
    servis = KategoriyaServisi(db)
    bolim = await servis.bolim_yaratish(malumot)
    return bolim


# ============== Holat boshqaruvi ==============

@router.post("/holat", summary="Yangi holat yaratish")
async def holat_yaratish(
    malumot: HolatYaratish,
    admin: Foydalanuvchi = Depends(admin_talab_qilish),
    db: AsyncSession = Depends(sessiya_olish)
):
    """Yangi klinik holat yaratadi."""
    servis = HolatServisi(db)
    holat = await servis.yaratish(malumot)
    
    # Bo'lim statistikasini yangilash
    kat_servis = KategoriyaServisi(db)
    await kat_servis.holatlar_sonini_yangilash(malumot.bolim_id)

    # Barcha foydalanuvchilarga bildirishnoma yuborish
    from servislar.bildirishnoma_servisi import BildirishnomServisi
    from modellar.bildirishnoma import BildirishnomaTuri
    
    bildirishnoma_servisi = BildirishnomServisi(db)
    await bildirishnoma_servisi.ommaviy_yaratish(
        turi=BildirishnomaTuri.YANGI_KONTENT,
        sarlavha="Yangi holat qoshildi!",
        matn=f"'{holat.sarlavha}' nomli yangi klinik holat platformaga qo'shildi. Hozir ko'rib chiqing!",
        havola=f"/holat/{holat.id}"
    )

    # Push notification (background)
    try:
        from vositalar.tasks import yangi_holat_push
        yangi_holat_push.delay(str(holat.id), holat.sarlavha)
    except Exception:
        pass
    
    return holat


@router.put("/holat/{holat_id}", summary="Holatni yangilash")
async def holat_yangilash(
    holat_id: UUID,
    malumot: HolatYangilash,
    admin: Foydalanuvchi = Depends(admin_talab_qilish),
    db: AsyncSession = Depends(sessiya_olish)
):
    """Holatni yangilaydi."""
    servis = HolatServisi(db)
    holat = await servis.yangilash(holat_id, malumot)
    
    if not holat:
        raise HTTPException(status_code=404, detail="Holat topilmadi")
    
    return holat


@router.delete("/holat/{holat_id}", response_model=MuvaffaqiyatJavob)
async def holat_ochirish(
    holat_id: UUID,
    admin: Foydalanuvchi = Depends(admin_talab_qilish),
    db: AsyncSession = Depends(sessiya_olish)
):
    """Holatni o'chiradi."""
    servis = HolatServisi(db)
    holat = await servis.olish(holat_id)
    
    if not holat:
        raise HTTPException(status_code=404, detail="Holat topilmadi")
    
    await servis._holat.ochirish(holat_id)
    return MuvaffaqiyatJavob(xabar="Holat o'chirildi")


# ============== Media yuklash ==============

@router.post("/media/rasm", summary="Rasm yuklash")
async def rasm_yuklash(
    fayl: UploadFile = File(...),
    jild: str = Query("medcase/rasmlar"),
    admin: Foydalanuvchi = Depends(admin_talab_qilish)
):
    """Cloudinary'ga rasm yuklaydi."""
    natija = await media_servisi.rasm_yuklash(fayl, jild)
    if not natija.get("muvaffaqiyat"):
        raise HTTPException(status_code=400, detail=natija.get("xato"))
    return natija


@router.post("/media/video", summary="Video yuklash")
async def video_yuklash(
    fayl: UploadFile = File(...),
    jild: str = Query("medcase/videolar"),
    admin: Foydalanuvchi = Depends(admin_talab_qilish)
):
    """Cloudinary'ga video yuklaydi."""
    natija = await media_servisi.video_yuklash(fayl, jild)
    if not natija.get("muvaffaqiyat"):
        raise HTTPException(status_code=400, detail=natija.get("xato"))
    return natija


@router.post("/media/tibbiy", summary="Tibbiy rasm yuklash")
async def tibbiy_rasm_yuklash(
    fayl: UploadFile = File(...),
    rasm_turi: str = Query("rentgen"),
    admin: Foydalanuvchi = Depends(admin_talab_qilish)
):
    """Tibbiy rasm (X-ray, CT, MRI) yuklaydi."""
    natija = await media_servisi.tibbiy_rasm_yuklash(fayl, rasm_turi)
    if not natija.get("muvaffaqiyat"):
        raise HTTPException(status_code=400, detail=natija.get("xato"))
    return natija


# ============== Foydalanuvchi boshqaruvi ==============

@router.get("/foydalanuvchilar", summary="Foydalanuvchilar ro'yxati")
async def foydalanuvchilar_royxati(
    sahifa: int = Query(1, ge=1),
    hajm: int = Query(20, ge=1, le=100),
    qidiruv: Optional[str] = None,
    rol: Optional[str] = None,
    faol: Optional[bool] = None,
    admin: Foydalanuvchi = Depends(admin_talab_qilish),
    db: AsyncSession = Depends(sessiya_olish)
):
    """Foydalanuvchilar ro'yxatini qaytaradi."""
    servis = FoydalanuvchiServisi(db)
    foydalanuvchilar, jami = await servis.admin_royxat(
        sahifa=sahifa, 
        hajm=hajm, 
        qidiruv=qidiruv,
        rol=rol,
        faol=faol
    )
    
    return {
        "foydalanuvchilar": foydalanuvchilar,
        "jami": jami,
        "sahifa": sahifa,
        "hajm": hajm,
        "sahifalar_soni": (jami + hajm - 1) // hajm if jami > 0 else 0
    }


@router.get("/foydalanuvchi/{foyd_id}", summary="Foydalanuvchi ma'lumotlari")
async def foydalanuvchi_olish(
    foyd_id: UUID,
    admin: Foydalanuvchi = Depends(admin_talab_qilish),
    db: AsyncSession = Depends(sessiya_olish)
):
    """Bitta foydalanuvchi to'liq ma'lumotlarini qaytaradi."""
    servis = FoydalanuvchiServisi(db)
    foydalanuvchi = await servis.id_bilan_olish(foyd_id)
    
    if not foydalanuvchi:
        raise HTTPException(status_code=404, detail="Foydalanuvchi topilmadi")
    
    return foydalanuvchi


@router.put("/foydalanuvchi/{foyd_id}", summary="Foydalanuvchini yangilash")
async def foydalanuvchi_yangilash(
    foyd_id: UUID,
    malumot: Dict[str, Any] = Body(...),
    admin: Foydalanuvchi = Depends(admin_talab_qilish),
    db: AsyncSession = Depends(sessiya_olish)
):
    """Foydalanuvchi ma'lumotlarini yangilaydi."""
    servis = FoydalanuvchiServisi(db)
    
    # Ruxsat etilgan maydonlar
    ruxsat_maydonlar = ['ism', 'familiya', 'rol', 'faol', 'email_tasdiqlangan']
    yangilash = {k: v for k, v in malumot.items() if k in ruxsat_maydonlar}
    
    if not yangilash:
        raise HTTPException(status_code=400, detail="Yangilash uchun ma'lumot berilmadi")
    
    foydalanuvchi = await servis.admin_yangilash(foyd_id, **yangilash)
    
    if not foydalanuvchi:
        raise HTTPException(status_code=404, detail="Foydalanuvchi topilmadi")
    
    return {"xabar": "Foydalanuvchi yangilandi", "foydalanuvchi": foydalanuvchi}


@router.put("/foydalanuvchi/{foyd_id}/rol", summary="Rol o'zgartirish")
async def rol_ozgartirish(
    foyd_id: UUID,
    yangi_rol: str = Body(..., embed=True),
    admin: Foydalanuvchi = Depends(admin_talab_qilish),
    db: AsyncSession = Depends(sessiya_olish)
):
    """Foydalanuvchi rolini o'zgartiradi."""
    servis = FoydalanuvchiServisi(db)
    foydalanuvchi = await servis.admin_yangilash(foyd_id, rol=yangi_rol)
    
    if not foydalanuvchi:
        raise HTTPException(status_code=404, detail="Foydalanuvchi topilmadi")
    
    return {"xabar": "Rol o'zgartirildi", "foydalanuvchi": foydalanuvchi}


@router.put("/foydalanuvchi/{foyd_id}/faollik", summary="Faollikni o'zgartirish")
async def faollik_ozgartirish(
    foyd_id: UUID,
    faol: bool = Body(..., embed=True),
    admin: Foydalanuvchi = Depends(admin_talab_qilish),
    db: AsyncSession = Depends(sessiya_olish)
):
    """Foydalanuvchini faollashtirish/bloklash."""
    servis = FoydalanuvchiServisi(db)
    foydalanuvchi = await servis.admin_yangilash(foyd_id, faol=faol)
    
    if not foydalanuvchi:
        raise HTTPException(status_code=404, detail="Foydalanuvchi topilmadi")
    
    holat = "faollashtirildi" if faol else "bloklandi"
    return {"xabar": f"Foydalanuvchi {holat}", "foydalanuvchi": foydalanuvchi}


@router.delete("/foydalanuvchi/{foyd_id}", response_model=MuvaffaqiyatJavob)
async def foydalanuvchi_ochirish(
    foyd_id: UUID,
    admin: Foydalanuvchi = Depends(admin_talab_qilish),
    db: AsyncSession = Depends(sessiya_olish)
):
    """Foydalanuvchini o'chiradi."""
    # O'zini o'zini o'chirishga ruxsat bermash
    if foyd_id == admin.id:
        raise HTTPException(status_code=400, detail="O'zingizni o'chira olmaysiz")
    
    servis = FoydalanuvchiServisi(db)
    await servis.ochirish(foyd_id)
    return MuvaffaqiyatJavob(xabar="Foydalanuvchi o'chirildi")


# ============== Kategoriya CRUD ==============

@router.post("/kategoriya/asosiy", summary="Asosiy kategoriya yaratish")
async def asosiy_kategoriya_yaratish(
    malumot: AsosiyKategoriyaYaratish,
    admin: Foydalanuvchi = Depends(admin_talab_qilish),
    db: AsyncSession = Depends(sessiya_olish)
):
    """Yangi asosiy kategoriya yaratadi."""
    servis = KategoriyaServisi(db)
    kategoriya = await servis.asosiy_kategoriya_yaratish(malumot)
    return {"xabar": "Kategoriya yaratildi", "kategoriya": kategoriya}


@router.put("/kategoriya/asosiy/{kat_id}", summary="Asosiy kategoriyani yangilash")
async def asosiy_kategoriya_yangilash(
    kat_id: UUID,
    malumot: AsosiyKategoriyaYangilash,
    admin: Foydalanuvchi = Depends(admin_talab_qilish),
    db: AsyncSession = Depends(sessiya_olish)
):
    """Asosiy kategoriyani yangilaydi."""
    servis = KategoriyaServisi(db)
    kategoriya = await servis.asosiy_kategoriya_yangilash(kat_id, malumot)
    if not kategoriya:
        raise HTTPException(status_code=404, detail="Kategoriya topilmadi")
    return {"xabar": "Kategoriya yangilandi", "kategoriya": kategoriya}


@router.delete("/kategoriya/asosiy/{kat_id}", response_model=MuvaffaqiyatJavob)
async def asosiy_kategoriya_ochirish(
    kat_id: UUID,
    admin: Foydalanuvchi = Depends(admin_talab_qilish),
    db: AsyncSession = Depends(sessiya_olish)
):
    """Asosiy kategoriyani o'chiradi."""
    servis = KategoriyaServisi(db)
    await servis.asosiy_kategoriya_ochirish(kat_id)
    return MuvaffaqiyatJavob(xabar="Kategoriya o'chirildi")


@router.post("/kategoriya/kichik", summary="Kichik kategoriya yaratish")
async def kichik_kategoriya_yaratish(
    malumot: KichikKategoriyaYaratish,
    admin: Foydalanuvchi = Depends(admin_talab_qilish),
    db: AsyncSession = Depends(sessiya_olish)
):
    """Yangi kichik kategoriya yaratadi."""
    servis = KategoriyaServisi(db)
    kategoriya = await servis.kichik_kategoriya_yaratish(malumot)
    return {"xabar": "Kichik kategoriya yaratildi", "kategoriya": kategoriya}


@router.put("/kategoriya/kichik/{kat_id}", summary="Kichik kategoriyani yangilash")
async def kichik_kategoriya_yangilash(
    kat_id: UUID,
    malumot: Dict[str, Any] = Body(...),
    admin: Foydalanuvchi = Depends(admin_talab_qilish),
    db: AsyncSession = Depends(sessiya_olish)
):
    """Kichik kategoriyani yangilaydi."""
    servis = KategoriyaServisi(db)
    kategoriya = await servis.kichik_kategoriya_yangilash(kat_id, malumot)
    if not kategoriya:
        raise HTTPException(status_code=404, detail="Kategoriya topilmadi")
    return {"xabar": "Kategoriya yangilandi", "kategoriya": kategoriya}


@router.delete("/kategoriya/kichik/{kat_id}", response_model=MuvaffaqiyatJavob)
async def kichik_kategoriya_ochirish(
    kat_id: UUID,
    admin: Foydalanuvchi = Depends(admin_talab_qilish),
    db: AsyncSession = Depends(sessiya_olish)
):
    """Kichik kategoriyani o'chiradi."""
    servis = KategoriyaServisi(db)
    await servis.kichik_kategoriya_ochirish(kat_id)
    return MuvaffaqiyatJavob(xabar="Kategoriya o'chirildi")


@router.post("/kategoriya/bolim", summary="Bo'lim yaratish")
async def bolim_yaratish(
    malumot: BolimYaratish,
    admin: Foydalanuvchi = Depends(admin_talab_qilish),
    db: AsyncSession = Depends(sessiya_olish)
):
    """Yangi bo'lim yaratadi."""
    servis = KategoriyaServisi(db)
    bolim = await servis.bolim_yaratish(malumot)
    return {"xabar": "Bo'lim yaratildi", "bolim": bolim}


@router.put("/kategoriya/bolim/{bolim_id}", summary="Bo'limni yangilash")
async def bolim_yangilash(
    bolim_id: UUID,
    malumot: Dict[str, Any] = Body(...),
    admin: Foydalanuvchi = Depends(admin_talab_qilish),
    db: AsyncSession = Depends(sessiya_olish)
):
    """Bo'limni yangilaydi."""
    servis = KategoriyaServisi(db)
    bolim = await servis.bolim_yangilash(bolim_id, malumot)
    if not bolim:
        raise HTTPException(status_code=404, detail="Bo'lim topilmadi")
    return {"xabar": "Bo'lim yangilandi", "bolim": bolim}


@router.delete("/kategoriya/bolim/{bolim_id}", response_model=MuvaffaqiyatJavob)
async def bolim_ochirish(
    bolim_id: UUID,
    admin: Foydalanuvchi = Depends(admin_talab_qilish),
    db: AsyncSession = Depends(sessiya_olish)
):
    """Bo'limni o'chiradi."""
    servis = KategoriyaServisi(db)
    await servis.bolim_ochirish(bolim_id)
    return MuvaffaqiyatJavob(xabar="Bo'lim o'chirildi")


# ============== Holat CRUD ==============

@router.delete("/holat/{holat_id}", response_model=MuvaffaqiyatJavob)
async def holat_ochirish(
    holat_id: UUID,
    admin: Foydalanuvchi = Depends(admin_talab_qilish),
    db: AsyncSession = Depends(sessiya_olish)
):
    """Holatni o'chiradi."""
    servis = HolatServisi(db)
    await servis.ochirish(holat_id)
    return MuvaffaqiyatJavob(xabar="Holat o'chirildi")


# ============== Excel Import ==============

@router.post("/import/excel/tahlil", summary="Excel faylni tahlil qilish")
async def excel_tahlil(
    fayl: UploadFile = File(..., description="Excel fayl (.xlsx)"),
    admin: Foydalanuvchi = Depends(admin_talab_qilish),
    db: AsyncSession = Depends(sessiya_olish)
):
    """
    Excel faylni tahlil qiladi va xatoliklarni tekshiradi.
    Import qilmasdan oldin faylni validatsiya qilish uchun.
    
    Excel ustunlari:
    - id: Holat identifikatori (ixtiyoriy)
    - section: Bo'lim nomi
    - main_category: Asosiy kategoriya
    - sub_category: Kichik kategoriya
    - case: Klinik holat matni
    - question: Savol
    - opt_a, opt_b, opt_c, opt_d: Javob variantlari
    - correct: To'g'ri javob (A, B, C, D)
    - expl_a, expl_b, expl_c, expl_d: Tushuntirishlar (ixtiyoriy)
    - diff: Qiyinlik darajasi (basic, intermediate, advanced)
    - link: Media havolasi (ixtiyoriy)
    """
    # Fayl turini tekshirish
    if not fayl.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Faqat Excel fayllar (.xlsx, .xls) qabul qilinadi"
        )
    
    # Fayl hajmini tekshirish (10MB max)
    content = await fayl.read()
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Fayl hajmi 10MB dan oshmasligi kerak"
        )
    
    servis = ImportServisi(db)
    natija = await servis.excel_tahlil_qilish(content)
    
    return natija


@router.post("/import/excel/import", summary="Excel dan import qilish")
async def excel_import(
    holatlar: List[Dict[str, Any]] = Body(..., description="Tahlil qilingan holatlar"),
    admin: Foydalanuvchi = Depends(admin_talab_qilish),
    db: AsyncSession = Depends(sessiya_olish)
):
    """
    Tahlil qilingan holatlarni bazaga import qiladi.
    Avval /import/excel/tahlil endpointidan holatlar ro'yxatini oling.
    """
    if not holatlar:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Holatlar ro'yxati bo'sh"
        )
    
    servis = ImportServisi(db)
    natija = await servis.excel_import_qilish(holatlar)
    
    return natija


@router.post("/import/excel/toliq", summary="Excel dan to'liq import")
async def excel_toliq_import(
    fayl: UploadFile = File(..., description="Excel fayl (.xlsx)"),
    admin: Foydalanuvchi = Depends(admin_talab_qilish),
    db: AsyncSession = Depends(sessiya_olish)
):
    """
    Excel faylni tahlil qiladi va xatolik bo'lmasa import qiladi.
    Bir qadamda tahlil va import.
    """
    # Fayl turini tekshirish
    if not fayl.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Faqat Excel fayllar (.xlsx, .xls) qabul qilinadi"
        )
    
    content = await fayl.read()
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Fayl hajmi 10MB dan oshmasligi kerak"
        )
    
    servis = ImportServisi(db)
    
    # Tahlil
    tahlil = await servis.excel_tahlil_qilish(content)
    
    if not tahlil.get("muvaffaqiyat"):
        return {
            "bosqich": "tahlil",
            "muvaffaqiyat": False,
            **tahlil
        }
    
    # Import
    holatlar = tahlil.get("holatlar", [])
    if not holatlar:
        return {
            "bosqich": "import",
            "muvaffaqiyat": False,
            "xato": "Import qilish uchun yaroqli holatlar topilmadi"
        }
    
    import_natija = await servis.excel_import_qilish(holatlar)
    
    return {
        "bosqich": "import",
        "tahlil": {
            "jami_qatorlar": tahlil.get("jami_qatorlar"),
            "yaroqli_holatlar": tahlil.get("yaroqli_holatlar"),
            "kategoriyalar": tahlil.get("kategoriyalar"),
        },
        **import_natija
    }


# ============== Statistika ==============

@router.get("/statistika", summary="Umumiy statistika")
async def umumiy_statistika(
    admin: Foydalanuvchi = Depends(admin_talab_qilish),
    db: AsyncSession = Depends(sessiya_olish)
):
    """Admin uchun umumiy platforma statistikasi."""
    foyd_servis = FoydalanuvchiServisi(db)
    kat_servis = KategoriyaServisi(db)
    
    foydalanuvchilar_soni = await foyd_servis.soni()
    kategoriya_stat = await kat_servis.toliq_statistika()
    
    return {
        "foydalanuvchilar_soni": foydalanuvchilar_soni,
        **kategoriya_stat
    }
