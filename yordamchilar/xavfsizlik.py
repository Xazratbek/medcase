# MedCase Pro Platform - Xavfsizlik Yordamchilari
# Parol hashlash va JWT token boshqaruvi
# OPTIMIZED: Faster bcrypt rounds, cached datetime

import logging
import hashlib
import bcrypt
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from functools import lru_cache

from sozlamalar.sozlamalar import sozlamalar

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def parol_hashlash(parol: str) -> str:
    """
    Parolni xavfsiz hashlaydi.
    ~100ms (rounds=10)

    FIX: Bcrypt 72 byte limitini aylanib o'tish uchun avval SHA-256 bilan hashlanadi.
    Bu har qanday uzunlikdagi parolni 64 baytlik xavfsiz qatorga aylantiradi.
    """
    # 1. SHA-256 pre-hashing (har doim 64 bayt hex digest)
    pre_hash = hashlib.sha256(parol.encode('utf-8')).hexdigest()

    # 2. Bcrypt hashing
    # rounds=10 (passlib configga mos)
    salt = bcrypt.gensalt(rounds=10)
    hashed = bcrypt.hashpw(pre_hash.encode('utf-8'), salt)

    return hashed.decode('utf-8')


def parol_tekshirish(parol: str, hash_str: str) -> bool:
    """
    Parolni hash bilan solishtiradi.
    ~100ms

    Backward Compatibility:
    1. Avval yangi usul (SHA-256 pre-hash) bilan tekshiradi.
    2. O'xshamasa, eski usul (legacy) bilan tekshirib ko'radi.
    """
    if not parol or not hash_str:
        return False

    try:
        # Kiruvchi hash string bo'lsa, bytes ga o'tkazamiz
        if isinstance(hash_str, str):
            hash_bytes = hash_str.encode('utf-8')
        else:
            hash_bytes = hash_str

        # 1-URINISH: Yangi tizim bo'yicha (SHA-256 pre-hash bilan)
        pre_hash = hashlib.sha256(parol.encode('utf-8')).hexdigest()
        try:
            if bcrypt.checkpw(pre_hash.encode('utf-8'), hash_bytes):
                return True
        except ValueError:
            pass

        # 2-URINISH: Eski tizim bo'yicha (Backward compatibility)
        # Passlib/Bcrypt eski versiyalari uzun parollarni truncate qilgan bo'lishi mumkin
        # Yoki shunchaki to'g'ridan-to'g'ri hashlangandir (agar < 72 bayt bo'lsa)

        # Original parolni bytega o'tkazamiz
        parol_bytes = parol.encode('utf-8')

        # Agar parol 72 baytdan oshsa, eski tizimda xato bergan bo'lishi kerak,
        # lekin juda eski bcrypt versiyalari buni jimgina truncate qilgan.
        # Biz har ehtimolga qarshi truncate qilingan versiyasini ham tekshiramiz.

        candidates = []

        # a) To'liq parol (agar <= 72 bayt bo'lsa, checkpw qabul qiladi)
        if len(parol_bytes) <= 72:
            candidates.append(parol_bytes)

        # b) Truncate qilingan parol (eski xatolarni/xususiyatlarni qo'llab-quvvatlash uchun)
        # Passlib character bo'yicha truncate qilgan bo'lishi mumkin (parol[:72])
        # Yoki bcrypt byte bo'yicha (parol_bytes[:72])

        # Character truncate (eski kodda parol[:72] bor edi)
        char_trunc = parol[:72].encode('utf-8')
        if char_trunc != parol_bytes and len(char_trunc) <= 72:
             candidates.append(char_trunc)

        # Byte truncate (bcrypt standard behavior)
        byte_trunc = parol_bytes[:72]
        if byte_trunc != parol_bytes and byte_trunc not in candidates:
             candidates.append(byte_trunc)

        for cand in candidates:
            try:
                if bcrypt.checkpw(cand, hash_bytes):
                    return True
            except ValueError:
                # Xato bo'lsa keyingisiga o'tamiz
                pass

        return False

    except Exception as e:
        logger.error(f"Parol tekshirishda xatolik: {e}")
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
