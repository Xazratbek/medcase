# MedCase Platform - API Marshrutlari
# Barcha API endpointlari

from fastapi import APIRouter

from marshrutlar.autentifikatsiya import router as autentifikatsiya_router
from marshrutlar.foydalanuvchi import router as foydalanuvchi_router
from marshrutlar.kategoriya import router as kategoriya_router
from marshrutlar.holat import router as holat_router
from marshrutlar.rivojlanish import router as rivojlanish_router
from marshrutlar.gamifikatsiya import router as gamifikatsiya_router
from marshrutlar.bildirishnoma import router as bildirishnoma_router
from marshrutlar.admin import router as admin_router
from marshrutlar.websocket import router as websocket_router
from marshrutlar.qidiruv import router as qidiruv_router
from marshrutlar.export import router as export_router
from marshrutlar.izoh import router as izoh_router
from marshrutlar.takrorlash import router as takrorlash_router
from marshrutlar.imtihon import router as imtihon_router
from marshrutlar.umumiy import router as umumiy_router

# Asosiy router
api_router = APIRouter()

# Marshrutlarni qo'shish
api_router.include_router(
    autentifikatsiya_router,
    prefix="/autentifikatsiya",
    tags=["Autentifikatsiya"]
)
api_router.include_router(
    foydalanuvchi_router,
    prefix="/foydalanuvchi",
    tags=["Foydalanuvchi"]
)
api_router.include_router(
    kategoriya_router,
    prefix="/kategoriya",
    tags=["Kategoriya"]
)
api_router.include_router(
    holat_router,
    prefix="/holat",
    tags=["Holatlar"]
)
api_router.include_router(
    rivojlanish_router,
    prefix="/rivojlanish",
    tags=["Rivojlanish"]
)
api_router.include_router(
    gamifikatsiya_router,
    prefix="/gamifikatsiya",
    tags=["Gamifikatsiya"]
)
api_router.include_router(
    bildirishnoma_router,
    prefix="/bildirishnoma",
    tags=["Bildirishnomalar"]
)
api_router.include_router(
    admin_router,
    prefix="/admin",
    tags=["Admin"]
)
api_router.include_router(
    websocket_router,
    tags=["WebSocket"]
)
api_router.include_router(
    qidiruv_router,
    prefix="/qidiruv",
    tags=["Qidiruv"]
)
api_router.include_router(
    export_router,
    prefix="/export",
    tags=["Export"]
)
api_router.include_router(
    izoh_router,
    prefix="/izoh",
    tags=["Izohlar"]
)
api_router.include_router(
    takrorlash_router,
    prefix="/takrorlash",
    tags=["Takrorlash"]
)
api_router.include_router(
    imtihon_router,
    prefix="/imtihon",
    tags=["Imtihon"]
)
api_router.include_router(
    umumiy_router,
    prefix="/umumiy",
    tags=["Umumiy"]
)

__all__ = ["api_router"]
