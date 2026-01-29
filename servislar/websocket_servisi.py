# MedCase Pro Platform - WebSocket Servisi
# Real-time xabarlar va bildirishnomalar uchun

from typing import Dict, List, Optional, Set
from uuid import UUID
from fastapi import WebSocket, WebSocketDisconnect
from datetime import datetime
import json
import asyncio
import logging

logger = logging.getLogger(__name__)


class WebSocketManager:
    """
    WebSocket ulanishlarini boshqaruvchi sinf.
    Foydalanuvchilarga real-time xabarlar yuborish uchun.
    """
    
    def __init__(self):
        # Foydalanuvchi ID -> WebSocket ulanishlari
        self._ulanishlar: Dict[str, Set[WebSocket]] = {}
        # Kanal obunalari (masalan: reyting, holat yangilanishlari)
        self._kanallar: Dict[str, Set[str]] = {}
        # Lock for thread safety
        self._lock = asyncio.Lock()
    
    async def ulash(self, websocket: WebSocket, foydalanuvchi_id: str) -> None:
        """Yangi WebSocket ulanishini qo'shadi."""
        await websocket.accept()
        
        async with self._lock:
            if foydalanuvchi_id not in self._ulanishlar:
                self._ulanishlar[foydalanuvchi_id] = set()
            self._ulanishlar[foydalanuvchi_id].add(websocket)
        
        logger.info(f"WebSocket ulandi: {foydalanuvchi_id}")
    
    async def uzish(self, websocket: WebSocket, foydalanuvchi_id: str) -> None:
        """WebSocket ulanishini o'chiradi."""
        async with self._lock:
            if foydalanuvchi_id in self._ulanishlar:
                self._ulanishlar[foydalanuvchi_id].discard(websocket)
                if not self._ulanishlar[foydalanuvchi_id]:
                    del self._ulanishlar[foydalanuvchi_id]
                    # Kanallardan ham o'chirish
                    for kanal in self._kanallar.values():
                        kanal.discard(foydalanuvchi_id)
        
        logger.info(f"WebSocket uzildi: {foydalanuvchi_id}")
    
    async def kanalga_obuna(self, foydalanuvchi_id: str, kanal: str) -> None:
        """Foydalanuvchini kanalga obuna qiladi."""
        async with self._lock:
            if kanal not in self._kanallar:
                self._kanallar[kanal] = set()
            self._kanallar[kanal].add(foydalanuvchi_id)
    
    async def kanaldan_chiqish(self, foydalanuvchi_id: str, kanal: str) -> None:
        """Foydalanuvchini kanaldan chiqaradi."""
        async with self._lock:
            if kanal in self._kanallar:
                self._kanallar[kanal].discard(foydalanuvchi_id)
    
    async def xabar_yuborish(
        self,
        foydalanuvchi_id: str,
        xabar: dict
    ) -> bool:
        """Bitta foydalanuvchiga xabar yuboradi."""
        ulanishlar = self._ulanishlar.get(foydalanuvchi_id, set())
        
        if not ulanishlar:
            return False
        
        xabar_json = json.dumps(xabar, ensure_ascii=False, default=str)
        uzilganlar = set()
        
        for ws in ulanishlar:
            try:
                await ws.send_text(xabar_json)
            except Exception as e:
                logger.warning(f"Xabar yuborishda xato: {e}")
                uzilganlar.add(ws)
        
        # Uzilgan ulanishlarni tozalash
        if uzilganlar:
            async with self._lock:
                for ws in uzilganlar:
                    self._ulanishlar.get(foydalanuvchi_id, set()).discard(ws)
        
        return True
    
    async def kanalga_xabar(self, kanal: str, xabar: dict) -> int:
        """Kanal obunachilarga xabar yuboradi."""
        obunchilar = self._kanallar.get(kanal, set())
        yuborildi = 0
        
        for foydalanuvchi_id in obunchilar:
            if await self.xabar_yuborish(foydalanuvchi_id, xabar):
                yuborildi += 1
        
        return yuborildi
    
    async def hammaga_xabar(self, xabar: dict) -> int:
        """Barcha ulangan foydalanuvchilarga xabar yuboradi."""
        yuborildi = 0
        
        for foydalanuvchi_id in list(self._ulanishlar.keys()):
            if await self.xabar_yuborish(foydalanuvchi_id, xabar):
                yuborildi += 1
        
        return yuborildi
    
    def ulangan_foydalanuvchilar_soni(self) -> int:
        """Ulangan foydalanuvchilar sonini qaytaradi."""
        return len(self._ulanishlar)
    
    def foydalanuvchi_ulangan(self, foydalanuvchi_id: str) -> bool:
        """Foydalanuvchi ulanganligini tekshiradi."""
        return foydalanuvchi_id in self._ulanishlar


# Global WebSocket manager
websocket_manager = WebSocketManager()


# ============== Xabar turlari ==============

class XabarTuri:
    """WebSocket xabar turlari."""
    BILDIRISHNOMA = "bildirishnoma"
    REYTING_YANGILASH = "reyting_yangilash"
    YANGI_NISHON = "yangi_nishon"
    DARAJA_OSHDI = "daraja_oshdi"
    STREAK_YANGILASH = "streak_yangilash"
    ONLAYN_FOYDALANUVCHILAR = "onlayn_foydalanuvchilar"
    XATO = "xato"
    ULANISH_TASDIQLANDI = "ulanish_tasdiqlandi"


def xabar_yaratish(turi: str, malumot: dict, sarlavha: str = None) -> dict:
    """Standart WebSocket xabar formati."""
    return {
        "turi": turi,
        "sarlavha": sarlavha,
        "malumot": malumot,
        "vaqt": datetime.utcnow().isoformat()
    }


# ============== Yordamchi funksiyalar ==============

async def bildirishnoma_yuborish(
    foydalanuvchi_id: str,
    sarlavha: str,
    matn: str,
    turi: str = "tizim",
    havola: str = None,
    qoshimcha: dict = None
) -> bool:
    """Foydalanuvchiga real-time bildirishnoma yuboradi."""
    xabar = xabar_yaratish(
        turi=XabarTuri.BILDIRISHNOMA,
        sarlavha=sarlavha,
        malumot={
            "matn": matn,
            "bildirishnoma_turi": turi,
            "havola": havola,
            **(qoshimcha or {})
        }
    )
    return await websocket_manager.xabar_yuborish(foydalanuvchi_id, xabar)


async def reyting_yangilash_yuborish(
    yangi_reyting: list,
    oldingi_uch: list = None
) -> int:
    """Reyting yangilanishini barcha obunchilarga yuboradi."""
    xabar = xabar_yaratish(
        turi=XabarTuri.REYTING_YANGILASH,
        sarlavha="Reyting yangilandi",
        malumot={
            "reyting": yangi_reyting,
            "oldingi_uch": oldingi_uch
        }
    )
    return await websocket_manager.kanalga_xabar("reyting", xabar)


async def nishon_yuborish(
    foydalanuvchi_id: str,
    nishon_nomi: str,
    nishon_rasmi: str = None,
    ball: int = 0
) -> bool:
    """Yangi nishon haqida xabar yuboradi."""
    xabar = xabar_yaratish(
        turi=XabarTuri.YANGI_NISHON,
        sarlavha="Yangi nishon! 🏆",
        malumot={
            "nishon_nomi": nishon_nomi,
            "nishon_rasmi": nishon_rasmi,
            "ball": ball
        }
    )
    return await websocket_manager.xabar_yuborish(foydalanuvchi_id, xabar)


async def daraja_oshdi_yuborish(
    foydalanuvchi_id: str,
    yangi_daraja: int,
    eski_daraja: int
) -> bool:
    """Daraja oshgani haqida xabar yuboradi."""
    xabar = xabar_yaratish(
        turi=XabarTuri.DARAJA_OSHDI,
        sarlavha=f"Tabriklaymiz! {yangi_daraja}-daraja 🎉",
        malumot={
            "yangi_daraja": yangi_daraja,
            "eski_daraja": eski_daraja
        }
    )
    return await websocket_manager.xabar_yuborish(foydalanuvchi_id, xabar)


async def streak_yangilash_yuborish(
    foydalanuvchi_id: str,
    joriy_streak: int,
    eng_uzun_streak: int
) -> bool:
    """Streak yangilanishi haqida xabar yuboradi."""
    xabar = xabar_yaratish(
        turi=XabarTuri.STREAK_YANGILASH,
        sarlavha="Streak yangilandi 🔥",
        malumot={
            "joriy_streak": joriy_streak,
            "eng_uzun_streak": eng_uzun_streak
        }
    )
    return await websocket_manager.xabar_yuborish(foydalanuvchi_id, xabar)
