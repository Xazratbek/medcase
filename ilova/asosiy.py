# MedCase Pro Platform - Asosiy FastAPI Ilovasi
# 2000-5000 concurrent users uchun optimallashtirilgan

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import time

from sozlamalar.sozlamalar import sozlamalar
from sozlamalar.malumotlar_bazasi import malumotlar_bazasi
from sozlamalar.redis_kesh import redis_kesh
from middleware.rate_limiter import rate_limiter, rate_limit_xato_ishlovchi
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
import hashlib

# Logger sozlash
logging.basicConfig(
    level=getattr(logging, sozlamalar.log_darajasi),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def hayot_sikli(app: FastAPI):
    """
    Ilova hayot sikli boshqaruvi.
    Ishga tushish va yopilishda resurslarni boshqaradi.
    """
    # Ishga tushish
    logger.info("MedCase Pro platformasi ishga tushmoqda...")

    # Ma'lumotlar bazasiga ulanish
    await malumotlar_bazasi.ulanish()
    logger.info("Ma'lumotlar bazasiga ulandi")

    # Redis'ga ulanish
    try:
        await redis_kesh.ulanish()
        logger.info("Redis serveriga ulandi")
    except Exception as e:
        logger.warning(f"Redis'ga ulanib bo'lmadi: {e}")

    logger.info("MedCase Pro platformasi tayyor!")

    yield

    # Yopilish
    logger.info("MedCase Pro platformasi yopilmoqda...")

    await malumotlar_bazasi.uzish()
    await redis_kesh.uzish()

    logger.info("MedCase Pro platformasi yopildi")


def ilova_yaratish() -> FastAPI:
    """
    FastAPI ilovasini yaratadi va sozlaydi.
    """
    app = FastAPI(
        title=sozlamalar.ilova_nomi,
        description="Tibbiyot talabalari va shifokorlar uchun interaktiv ta'lim platformasi",
        version=sozlamalar.ilova_versiyasi,
        docs_url="/hujjatlar" if sozlamalar.debug else None,
        redoc_url="/qayta-hujjatlar" if sozlamalar.debug else None,
        openapi_url="/openapi.json" if sozlamalar.debug else None,
        lifespan=hayot_sikli
    )

    # ============== Middleware ==============

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=sozlamalar.cors_manbalar_royxati,
        allow_credentials=True,
        allow_methods=sozlamalar.cors_metodlar_royxati,
        allow_headers=sozlamalar.cors_sarlavhalar_royxati
    )

    # GZip siqish (javoblar uchun)
    app.add_middleware(GZipMiddleware, minimum_size=1000)

    # Anti-abuse (bir xil so'rovlarni ko'p yuborishni bloklash)
    @app.middleware("http")
    async def abuse_himoya_middleware(request: Request, call_next):
        if not sozlamalar.abuse_block_enabled:
            return await call_next(request)

        ip = get_remote_address(request)
        if not ip:
            return await call_next(request)

        block_key = f"abuse:block:{ip}"
        if await redis_kesh.mavjud(block_key):
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "muvaffaqiyat": False,
                    "xato": "Ko'p takroriy so'rovlar. Vaqtinchalik bloklandi",
                    "xato_kodi": "ABUSE_BLOCKED"
                }
            )

        signature = f"{request.method}:{request.url.path}?{request.url.query}"
        sig_hash = hashlib.md5(signature.encode()).hexdigest()[:16]
        count_key = f"abuse:count:{ip}:{sig_hash}"
        count = await redis_kesh.oshirish_va_muddat(
            count_key,
            sozlamalar.abuse_block_window_seconds
        )
        if count >= sozlamalar.abuse_block_threshold:
            await redis_kesh.saqlash(
                block_key,
                {"sababi": "takroriy_so'rovlar"},
                sozlamalar.abuse_block_duration_seconds
            )
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "muvaffaqiyat": False,
                    "xato": "Ko'p takroriy so'rovlar. 10 soatga bloklandi",
                    "xato_kodi": "ABUSE_BLOCKED"
                }
            )

        return await call_next(request)

    # Rate Limiter (ixtiyoriy)
    if sozlamalar.rate_limit_enabled:
        app.state.limiter = rate_limiter
        app.add_exception_handler(RateLimitExceeded, rate_limit_xato_ishlovchi)

    # ============== So'rov/Javob Middleware ==============

    @app.middleware("http")
    async def sorov_vaqti_middleware(request: Request, call_next):
        """So'rov vaqtini o'lchaydi va log qiladi."""
        boshlash = time.time()

        response = await call_next(request)

        davomiylik = time.time() - boshlash
        response.headers["X-Javob-Vaqti"] = f"{davomiylik:.4f}"

        # Sekin so'rovlarni log qilish
        if davomiylik > 1.0:
            logger.warning(
                f"Sekin so'rov: {request.method} {request.url.path} - {davomiylik:.2f}s"
            )

        return response

    @app.middleware("http")
    async def xavfsizlik_sarlavhalari(request: Request, call_next):
        """Xavfsizlik sarlavhalarini qo'shadi."""
        response = await call_next(request)

        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

        return response

    # ============== Xato Ishlovchilari ==============

    @app.exception_handler(RequestValidationError)
    async def validation_xato_ishlovchi(request: Request, exc: RequestValidationError):
        """Validation xatolarini ushlaydi va chiroyli javob qaytaradi."""
        logger.warning(f"Validation xatosi: {exc.errors()}")

        errors = []
        for err in exc.errors():
            # Pydantic xatolarida ba'zan serializatsiya bo'lmaydigan ob'ektlar bo'ladi (masalan ValueError)
            cleaned_err = dict(err)
            if "ctx" in cleaned_err:
                cleaned_ctx = dict(cleaned_err["ctx"])
                for k, v in cleaned_ctx.items():
                    if isinstance(v, Exception):
                        cleaned_ctx[k] = str(v)
                cleaned_err["ctx"] = cleaned_ctx
            errors.append(cleaned_err)

        # Birinchi xatoni olish
        xato_matni = "Ma'lumotlar noto'g'ri kiritilgan"
        if errors:
            error = errors[0]
            field = " -> ".join([str(loc) for loc in error["loc"][1:]])
            msg = error["msg"]
            xato_matni = f"{field}: {msg}" if field else msg

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=jsonable_encoder({
                "muvaffaqiyat": False,
                "xato": xato_matni,
                "xato_kodi": "VALIDATION_ERROR",
                "tafsilotlar": errors
            })
        )

    @app.exception_handler(Exception)
    async def umumiy_xato_ishlovchi(request: Request, exc: Exception):
        """Barcha kutilmagan xatolarni ushlaydi."""
        logger.error(f"Kutilmagan xato: {exc}", exc_info=True)

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "muvaffaqiyat": False,
                "xato": "Ichki server xatosi",
                "xato_kodi": "INTERNAL_ERROR"
            }
        )

    # ============== Marshrutlar ==============

    from marshrutlar import api_router
    app.include_router(api_router, prefix="/api/v1")

    # ============== Sog'liqni Tekshirish ==============

    @app.get("/", tags=["Tizim"])
    async def ildiz():
        """Asosiy endpoint - ilova ishlayotganini tekshirish."""
        return {
            "ilova": sozlamalar.ilova_nomi,
            "versiya": sozlamalar.ilova_versiyasi,
            "holat": "ishlayapti"
        }

    @app.get("/sogliq", tags=["Tizim"])
    async def sogliq_tekshiruvi():
        """Tizim sog'lig'ini tekshiradi."""
        natija = {
            "holat": "soglom",
            "komponentlar": {}
        }

        # Ma'lumotlar bazasi
        try:
            if malumotlar_bazasi.ulangan:
                natija["komponentlar"]["malumotlar_bazasi"] = "soglom"
            else:
                natija["komponentlar"]["malumotlar_bazasi"] = "ulanmagan"
                natija["holat"] = "qisman"
        except:
            natija["komponentlar"]["malumotlar_bazasi"] = "xato"
            natija["holat"] = "nosoglom"

        # Redis
        try:
            if await redis_kesh.mavjud("test"):
                pass
            natija["komponentlar"]["redis"] = "soglom"
        except:
            natija["komponentlar"]["redis"] = "ulanmagan"

        return natija

    @app.get("/statistika", tags=["Tizim"])
    async def tizim_statistikasi():
        """Tizim statistikasini qaytaradi (admin uchun)."""
        return {
            "muhit": sozlamalar.muhit,
            "debug": sozlamalar.debug,
            "versiya": sozlamalar.ilova_versiyasi
        }

    return app


# Global ilova ob'ekti
ilova = ilova_yaratish()
