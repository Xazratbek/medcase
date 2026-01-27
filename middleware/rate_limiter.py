# MedCase Platform - Rate Limiter Middleware
# So'rovlar sonini cheklash (2k-5k user uchun optimallashtirilgan)

from fastapi import Request, HTTPException, status
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from starlette.responses import JSONResponse

from sozlamalar.sozlamalar import sozlamalar


def kalit_funksiyasi(request: Request) -> str:
    """
    Rate limit kalitini aniqlaydi.
    Autentifikatsiya qilingan foydalanuvchi uchun user_id,
    Anonim uchun IP manzil ishlatiladi.
    """
    # Authorization headerdan foydalanuvchi olishga harakat
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        # Token mavjud - foydalanuvchi ID ishlatiladi
        from yordamchilar.xavfsizlik import token_dekodlash
        token = auth_header.split(" ")[1]
        payload = token_dekodlash(token)
        if payload and "foydalanuvchi_id" in payload:
            return f"user:{payload['foydalanuvchi_id']}"
    
    # Anonim - IP manzil
    return f"ip:{get_remote_address(request)}"


# Rate limiter yaratish
rate_limiter = Limiter(
    key_func=kalit_funksiyasi,
    default_limits=[
        f"{sozlamalar.rate_limit_per_minute}/minute",
        f"{sozlamalar.rate_limit_per_hour}/hour"
    ],
    storage_uri=sozlamalar.redis_url,
    strategy="fixed-window"
)


async def rate_limit_xato_ishlovchi(request: Request, exc: RateLimitExceeded):
    """Rate limit xatosi uchun maxsus javob."""
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={
            "muvaffaqiyat": False,
            "xato": "So'rovlar soni chegaradan oshdi",
            "xato_kodi": "RATE_LIMIT_EXCEEDED",
            "tafsilotlar": {
                "limit": str(exc.detail),
                "qayta_urinish": "1 daqiqadan so'ng qayta urining"
            }
        }
    )


# Maxsus rate limitlar
class MaxsusLimitlar:
    """Turli endpointlar uchun maxsus limitlar."""
    
    # Autentifikatsiya - qattiqroq limit
    KIRISH = "5/minute"
    ROYXATDAN_OTISH = "3/minute"
    PAROL_TIKLASH = "3/minute"
    
    # API - standart limit
    STANDART = "60/minute"
    
    # Og'ir operatsiyalar - past limit
    MEDIA_YUKLASH = "10/minute"
    EXPORT = "5/minute"
    
    # Yengil operatsiyalar - yuqori limit
    QIDIRUV = "100/minute"
    OLISH = "200/minute"
