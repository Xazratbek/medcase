# MedCase Pro Platform - Umumiy Vositalar
# Yordamchi funksiyalar to'plami

import re
import secrets
import string
from datetime import datetime, timedelta
from typing import Tuple


def slug_yaratish(matn: str) -> str:
    """
    Matнdan URL uchun mos slug yaratadi.
    O'zbek harflarini ham qo'llab-quvvatlaydi.
    """
    # Kichik harflarga o'tkazish
    slug = matn.lower()
    
    # O'zbek harflarini almashtirish
    almashtirishlar = {
        "o'": "o", "o`": "o", "oʻ": "o",
        "g'": "g", "g`": "g", "gʻ": "g",
        "sh": "sh", "ch": "ch",
        "а": "a", "б": "b", "в": "v", "г": "g", "д": "d",
        "е": "e", "ё": "yo", "ж": "j", "з": "z", "и": "i",
        "й": "y", "к": "k", "л": "l", "м": "m", "н": "n",
        "о": "o", "п": "p", "р": "r", "с": "s", "т": "t",
        "у": "u", "ф": "f", "х": "x", "ц": "ts", "ч": "ch",
        "ш": "sh", "щ": "sch", "ъ": "", "ы": "i", "ь": "",
        "э": "e", "ю": "yu", "я": "ya"
    }
    
    for qidirish, almashtirish in almashtirishlar.items():
        slug = slug.replace(qidirish, almashtirish)
    
    # Faqat harflar, raqamlar va tire qoldirish
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    
    # Bo'shliqlarni tire bilan almashtirish
    slug = re.sub(r"[\s_]+", "-", slug)
    
    # Ketma-ket tirelerni bitta qilish
    slug = re.sub(r"-+", "-", slug)
    
    # Bosh va oxiridagi tirelerni olib tashlash
    slug = slug.strip("-")
    
    return slug


def tasodifiy_kod_yaratish(uzunlik: int = 6, faqat_raqam: bool = False) -> str:
    """
    Tasodifiy kod yaratadi (tasdiqlash kodlari uchun).
    """
    if faqat_raqam:
        belgilar = string.digits
    else:
        belgilar = string.ascii_uppercase + string.digits
    
    return "".join(secrets.choice(belgilar) for _ in range(uzunlik))


def vaqt_formatlash(vaqt: datetime, format: str = "to'liq") -> str:
    """
    Vaqtni o'zbek tilida formatlaydi.
    """
    oylar = [
        "", "Yanvar", "Fevral", "Mart", "Aprel", "May", "Iyun",
        "Iyul", "Avgust", "Sentyabr", "Oktyabr", "Noyabr", "Dekabr"
    ]
    
    if format == "to'liq":
        return f"{vaqt.day} {oylar[vaqt.month]} {vaqt.year}, {vaqt.hour:02d}:{vaqt.minute:02d}"
    elif format == "sana":
        return f"{vaqt.day} {oylar[vaqt.month]} {vaqt.year}"
    elif format == "qisqa":
        return f"{vaqt.day:02d}.{vaqt.month:02d}.{vaqt.year}"
    elif format == "vaqt":
        return f"{vaqt.hour:02d}:{vaqt.minute:02d}"
    else:
        return str(vaqt)


def vaqt_oldin_formatlash(vaqt: datetime) -> str:
    """
    Vaqtni 'X oldin' formatida qaytaradi.
    """
    hozir = datetime.utcnow()
    farq = hozir - vaqt
    
    soniyalar = int(farq.total_seconds())
    
    if soniyalar < 60:
        return "hozirgina"
    elif soniyalar < 3600:
        daqiqalar = soniyalar // 60
        return f"{daqiqalar} daqiqa oldin"
    elif soniyalar < 86400:
        soatlar = soniyalar // 3600
        return f"{soatlar} soat oldin"
    elif soniyalar < 604800:
        kunlar = soniyalar // 86400
        return f"{kunlar} kun oldin"
    elif soniyalar < 2592000:
        haftalar = soniyalar // 604800
        return f"{haftalar} hafta oldin"
    else:
        return vaqt_formatlash(vaqt, "sana")


def sahifalash_hisoblash(
    jami: int,
    sahifa: int,
    hajm: int
) -> Tuple[int, int, int, bool, bool]:
    """
    Sahifalash ma'lumotlarini hisoblaydi.
    
    Returns:
        (sahifalar_soni, offset, limit, oldingi_bor, keyingi_bor)
    """
    sahifalar_soni = (jami + hajm - 1) // hajm if hajm > 0 else 0
    offset = (sahifa - 1) * hajm
    
    oldingi_bor = sahifa > 1
    keyingi_bor = sahifa < sahifalar_soni
    
    return sahifalar_soni, offset, hajm, oldingi_bor, keyingi_bor


def soniyalarni_formatlash(soniyalar: int) -> str:
    """
    Soniyalarni o'qilishi oson formatga o'zgartiradi.
    """
    if soniyalar < 60:
        return f"{soniyalar} soniya"
    elif soniyalar < 3600:
        daqiqalar = soniyalar // 60
        qoldiq = soniyalar % 60
        if qoldiq > 0:
            return f"{daqiqalar} daqiqa {qoldiq} soniya"
        return f"{daqiqalar} daqiqa"
    else:
        soatlar = soniyalar // 3600
        qoldiq_daqiqa = (soniyalar % 3600) // 60
        if qoldiq_daqiqa > 0:
            return f"{soatlar} soat {qoldiq_daqiqa} daqiqa"
        return f"{soatlar} soat"


def foizni_hisoblash(qism: int, butun: int, kasr: int = 1) -> float:
    """
    Foizni xavfsiz hisoblaydi (0 ga bo'lishdan himoya).
    """
    if butun == 0:
        return 0.0
    return round((qism / butun) * 100, kasr)
