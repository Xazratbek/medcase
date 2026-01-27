# MedCase Platform - Umumiy Marshrutlar

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from sozlamalar.malumotlar_bazasi import sessiya_olish
from servislar.kategoriya_servisi import KategoriyaServisi
from servislar.foydalanuvchi_servisi import FoydalanuvchiServisi
from servislar.holat_servisi import HolatServisi

router = APIRouter()


@router.get("/landing-data", summary="Landing page uchun ma'lumotlar")
async def get_landing_data(db: AsyncSession = Depends(sessiya_olish)):
    """
    Landing page uchun kerakli ma'lumotlarni qaytaradi.
    """
    kategoriya_servisi = KategoriyaServisi(db)
    foydalanuvchi_servisi = FoydalanuvchiServisi(db)
    holat_servisi = HolatServisi(db)

    # Features
    features = [
        {
            "icon": "HiOutlineAcademicCap",
            "title": "Klinik holatlar",
            "description": "5000+ real klinik stsenariylar asosida o'rganing",
            "color": "from-med-400 to-med-600"
        },
        {
            "icon": "HiOutlineChartBar",
            "title": "Rivojlanish kuzatuvi",
            "description": "Shaxsiy statistika va zaif tomonlaringizni aniqlang",
            "color": "from-blue-400 to-blue-600"
        },
        {
            "icon": "HiOutlineLightningBolt",
            "title": "Gamifikatsiya",
            "description": "Ballar, nishonlar va reytinglar bilan motivatsiya",
            "color": "from-gold-400 to-gold-600"
        },
        {
            "icon": "HiOutlineUserGroup",
            "title": "Hamjamiyat",
            "description": "Minglab shifokor va talabalar bilan birga o'qing",
            "color": "from-purple-400 to-purple-600"
        },
    ]

    # Stats
    holatlar_soni = await holat_servisi.soni()
    kategoriyalar_soni = await kategoriya_servisi.asosiy_kategoriya_soni()
    foydalanuvchilar_soni = await foydalanuvchi_servisi.soni()

    stats = [
        {"value": f"{holatlar_soni}+", "label": "Klinik holatlar"},
        {"value": f"{kategoriyalar_soni}+", "label": "Kategoriyalar"},
        {"value": f"{foydalanuvchilar_soni}+", "label": "Foydalanuvchilar"},
        {"value": "95%", "label": "Qoniqish darajasi"},
    ]

    # Categories
    eng_kop_holatli_kategoriyalar = await kategoriya_servisi.eng_kop_holatli_kategoriyalar(limit=6)
    
    categories = [
        {
            "name": kat.nomi,
            "count": kat.holatlar_soni,
            "emoji": kat.ikonka,
        }
        for kat in eng_kop_holatli_kategoriyalar
    ]

    return {
        "features": features,
        "stats": stats,
        "categories": categories,
    }
