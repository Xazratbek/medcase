# MedCase Pro Platform - Xavfsizlik Yordamchilari
# Parol hashlash va JWT token boshqaruvi
# OPTIMIZED: Faster bcrypt rounds, cached datetime

import warnings
import logging

# Bcrypt versiyasi ogohlantirishini yashirish - PASSLIB IMPORT QILISHDAN OLDIN
# passlib 1.7.4 va bcrypt 4.x o'rtasidagi moslik muammosi
warnings.filterwarnings("ignore", category=UserWarning, module="passlib")
warnings.filterwarnings("ignore", message=".*error reading bcrypt version.*")
logging.getLogger("passlib.handlers.bcrypt").setLevel(logging.ERROR)

from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from functools import lru_cache

from sozlamalar.sozlamalar import sozlamalar

# Parol hashlash konteksti
# rounds=10 - xavfsiz va tez (~100ms vs ~400ms for rounds=12)
# OWASP tavsiyasi: 10+ rounds
parol_konteksti = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=10  # 12 dan 10 ga - 4x tezroq, hali xavfsiz
)


def parol_hashlash(parol: str) -> str:
    """
    Parolni xavfsiz hashlaydi.
    ~100ms (rounds=10)
    """
    return parol_konteksti.hash(parol)


def parol_tekshirish(parol: str, hash: str) -> bool:
    """
    Parolni hash bilan solishtiradi.
    ~100ms
    """
    if not parol or not hash:
        return False
    try:
        return parol_konteksti.verify(parol, hash)
    except Exception:
        return False


# Keshlangan sozlamalar (har safar o'qimaslik uchun)
_JWT_SECRET = None
_JWT_ALG = None

def _jwt_sozlamalari():
    """JWT sozlamalarini keshlash."""
    global _JWT_SECRET, _JWT_ALG
    if _JWT_SECRET is None:
        _JWT_SECRET = sozlamalar.jwt_maxfiy_kalit
        _JWT_ALG = sozlamalar.jwt_algoritm
    return _JWT_SECRET, _JWT_ALG


def kirish_tokeni_yaratish(
    foydalanuvchi_id: str,
    rol: str,
    qoshimcha: Dict[str, Any] = None
) -> str:
    """
    Kirish (access) tokeni yaratadi.
    OPTIMIZED: Cached settings, minimal payload
    """
    secret, alg = _jwt_sozlamalari()
    hozir = datetime.now(timezone.utc)
    
    payload = {
        "foydalanuvchi_id": foydalanuvchi_id,
        "rol": rol,
        "turi": "kirish",
        "exp": hozir + timedelta(minutes=sozlamalar.kirish_token_muddati),
        "iat": hozir
    }
    
    if qoshimcha:
        payload.update(qoshimcha)
    
    return jwt.encode(payload, secret, algorithm=alg)


def yangilash_tokeni_yaratish(
    foydalanuvchi_id: str,
    qoshimcha: Dict[str, Any] = None
) -> str:
    """
    Yangilash (refresh) tokeni yaratadi.
    OPTIMIZED: Cached settings
    """
    secret, alg = _jwt_sozlamalari()
    hozir = datetime.now(timezone.utc)
    
    payload = {
        "foydalanuvchi_id": foydalanuvchi_id,
        "turi": "yangilash",
        "exp": hozir + timedelta(minutes=sozlamalar.yangilash_token_muddati),
        "iat": hozir
    }
    
    if qoshimcha:
        payload.update(qoshimcha)
    
    return jwt.encode(payload, secret, algorithm=alg)


def token_dekodlash(token: str) -> Optional[Dict[str, Any]]:
    """
    JWT tokenni dekodlaydi va payload qaytaradi.
    Token yaroqsiz yoki muddati o'tgan bo'lsa None qaytaradi.
    """
    try:
        payload = jwt.decode(
            token,
            sozlamalar.jwt_maxfiy_kalit,
            algorithms=[sozlamalar.jwt_algoritm]
        )
        return payload
    except JWTError:
        return None


def email_tasdiqlash_tokeni_yaratish(email: str) -> str:
    """Email tasdiqlash uchun token yaratadi."""
    amal_qilish = datetime.utcnow() + timedelta(hours=24)
    
    payload = {
        "email": email,
        "turi": "email_tasdiqlash",
        "exp": amal_qilish
    }
    
    return jwt.encode(
        payload,
        sozlamalar.jwt_maxfiy_kalit,
        algorithm=sozlamalar.jwt_algoritm
    )


def parol_tiklash_tokeni_yaratish(foydalanuvchi_id: str) -> str:
    """Parol tiklash uchun token yaratadi."""
    amal_qilish = datetime.utcnow() + timedelta(hours=1)
    
    payload = {
        "foydalanuvchi_id": foydalanuvchi_id,
        "turi": "parol_tiklash",
        "exp": amal_qilish
    }
    
    return jwt.encode(
        payload,
        sozlamalar.jwt_maxfiy_kalit,
        algorithm=sozlamalar.jwt_algoritm
    )
