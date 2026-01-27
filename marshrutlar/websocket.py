# MedCase Platform - WebSocket Marshrutlari
# Real-time ulanishlar uchun

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, Depends
from typing import Optional
import json
import logging

from servislar.websocket_servisi import (
    websocket_manager,
    XabarTuri,
    xabar_yaratish
)
from yordamchilar.xavfsizlik import token_dekodlash

logger = logging.getLogger(__name__)
router = APIRouter()


async def websocket_autentifikatsiya(token: str) -> Optional[dict]:
    """WebSocket uchun token tekshirish."""
    if not token:
        return None
    
    payload = token_dekodlash(token)
    if not payload:
        return None
    
    return payload


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str = Query(None)
):
    """
    Asosiy WebSocket endpoint.
    
    Ulanish: ws://server/api/v1/ws?token=JWT_TOKEN
    
    Xabar formatlari:
    - Serverdan: {"turi": "...", "sarlavha": "...", "malumot": {...}, "vaqt": "..."}
    - Klientdan: {"amal": "obuna", "kanal": "reyting"}
    """
    # Autentifikatsiya
    payload = await websocket_autentifikatsiya(token)
    
    if not payload:
        await websocket.close(code=4001, reason="Autentifikatsiya muvaffaqiyatsiz")
        return
    
    foydalanuvchi_id = payload.get("foydalanuvchi_id")
    
    if not foydalanuvchi_id:
        await websocket.close(code=4001, reason="Foydalanuvchi ID topilmadi")
        return
    
    # Ulanish
    await websocket_manager.ulash(websocket, foydalanuvchi_id)
    
    try:
        # Ulanish tasdiqlash xabari
        tasdiqlash = xabar_yaratish(
            turi=XabarTuri.ULANISH_TASDIQLANDI,
            sarlavha="Ulanish muvaffaqiyatli",
            malumot={
                "foydalanuvchi_id": foydalanuvchi_id,
                "onlayn_soni": websocket_manager.ulangan_foydalanuvchilar_soni()
            }
        )
        await websocket.send_json(tasdiqlash)
        
        # Xabarlarni tinglash
        while True:
            try:
                data = await websocket.receive_text()
                xabar = json.loads(data)
                
                amal = xabar.get("amal")
                
                if amal == "obuna":
                    # Kanalga obuna bo'lish
                    kanal = xabar.get("kanal")
                    if kanal:
                        await websocket_manager.kanalga_obuna(foydalanuvchi_id, kanal)
                        await websocket.send_json({
                            "turi": "obuna_tasdiqlandi",
                            "kanal": kanal
                        })
                
                elif amal == "obunadan_chiqish":
                    # Kanaldan chiqish
                    kanal = xabar.get("kanal")
                    if kanal:
                        await websocket_manager.kanaldan_chiqish(foydalanuvchi_id, kanal)
                        await websocket.send_json({
                            "turi": "obunadan_chiqildi",
                            "kanal": kanal
                        })
                
                elif amal == "ping":
                    # Keep-alive
                    await websocket.send_json({"turi": "pong"})
                
            except json.JSONDecodeError:
                await websocket.send_json({
                    "turi": XabarTuri.XATO,
                    "xabar": "Noto'g'ri JSON format"
                })
                
    except WebSocketDisconnect:
        logger.info(f"WebSocket uzildi: {foydalanuvchi_id}")
    except Exception as e:
        logger.error(f"WebSocket xatosi: {e}")
    finally:
        await websocket_manager.uzish(websocket, foydalanuvchi_id)


@router.get("/ws/statistika")
async def websocket_statistika():
    """WebSocket statistikasi (admin uchun)."""
    return {
        "ulangan_foydalanuvchilar": websocket_manager.ulangan_foydalanuvchilar_soni()
    }
