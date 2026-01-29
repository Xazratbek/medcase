# MedCase Pro Platform - Redis Keshlash Konfiguratsiyasi
# 2000-5000 foydalanuvchi uchun optimallashtirilgan keshlash

import redis.asyncio as redis
from typing import Optional, Any, Union
import json
import logging
from functools import wraps
import hashlib

from sozlamalar.sozlamalar import sozlamalar

logger = logging.getLogger(__name__)


class RedisKesh:
    """
    Redis bilan keshlash operatsiyalari.
    High-performance keshlash 2k-5k concurrent users uchun.
    """
    
    def __init__(self):
        self._redis: Optional[redis.Redis] = None
        self._pool: Optional[redis.ConnectionPool] = None
    
    async def ulanish(self) -> None:
        """Redis serveriga ulanadi."""
        if self._redis is None:
            logger.info("Redis serveriga ulanish...")
            
            self._pool = redis.ConnectionPool.from_url(
                sozlamalar.redis_url,
                password=sozlamalar.redis_parol,
                max_connections=50,
                decode_responses=True,
                socket_timeout=5,
                socket_connect_timeout=5,
                retry_on_timeout=True,
            )
            
            self._redis = redis.Redis(connection_pool=self._pool)
            
            # Ulanishni tekshirish
            await self._redis.ping()
            logger.info("Redis serveriga muvaffaqiyatli ulandi")
    
    async def uzish(self) -> None:
        """Redis ulanishini yopadi."""
        if self._redis is not None:
            await self._redis.close()
            if self._pool:
                await self._pool.disconnect()
            self._redis = None
            self._pool = None
            logger.info("Redis ulanishi yopildi")
    
    async def olish(self, kalit: str) -> Optional[Any]:
        """Keshdan qiymat oladi."""
        if self._redis is None:
            await self.ulanish()
        
        try:
            qiymat = await self._redis.get(kalit)
            if qiymat:
                return json.loads(qiymat)
            return None
        except Exception as xato:
            logger.error(f"Redis olish xatosi: {xato}")
            return None
    
    async def saqlash(
        self,
        kalit: str,
        qiymat: Any,
        muddati: int = None
    ) -> bool:
        """Keshga qiymat saqlaydi."""
        if self._redis is None:
            await self.ulanish()
        
        try:
            muddati = muddati or sozlamalar.kesh_ttl
            await self._redis.setex(
                kalit,
                muddati,
                json.dumps(qiymat, ensure_ascii=False, default=str)
            )
            return True
        except Exception as xato:
            logger.error(f"Redis saqlash xatosi: {xato}")
            return False
    
    async def ochirish(self, kalit: str) -> bool:
        """Keshdan qiymatni o'chiradi."""
        if self._redis is None:
            await self.ulanish()
        
        try:
            await self._redis.delete(kalit)
            return True
        except Exception as xato:
            logger.error(f"Redis ochirish xatosi: {xato}")
            return False
    
    async def shablon_ochirish(self, shablon: str) -> int:
        """Shablon bo'yicha kalitlarni o'chiradi."""
        if self._redis is None:
            await self.ulanish()
        
        try:
            kalitlar = []
            async for kalit in self._redis.scan_iter(match=shablon):
                kalitlar.append(kalit)
            
            if kalitlar:
                await self._redis.delete(*kalitlar)
            return len(kalitlar)
        except Exception as xato:
            logger.error(f"Shablon ochirish xatosi: {xato}")
            return 0
    
    async def oshirish(self, kalit: str, qiymat: int = 1) -> int:
        """Raqamli qiymatni oshiradi."""
        if self._redis is None:
            await self.ulanish()
        
        try:
            return await self._redis.incrby(kalit, qiymat)
        except Exception as xato:
            logger.error(f"Redis oshirish xatosi: {xato}")
            return 0

    async def oshirish_va_muddat(
        self,
        kalit: str,
        muddati: int,
        qiymat: int = 1
    ) -> int:
        """Raqamli qiymatni oshiradi va birinchi oshirishda TTL beradi."""
        if self._redis is None:
            await self.ulanish()

        try:
            yangi_qiymat = await self._redis.incrby(kalit, qiymat)
            if yangi_qiymat == qiymat:
                await self._redis.expire(kalit, muddati)
            return yangi_qiymat
        except Exception as xato:
            logger.error(f"Redis oshirish/muddat xatosi: {xato}")
            return 0
    
    async def mavjud(self, kalit: str) -> bool:
        """Kalit mavjudligini tekshiradi."""
        if self._redis is None:
            await self.ulanish()
        
        try:
            return await self._redis.exists(kalit) > 0
        except Exception as xato:
            logger.error(f"Redis mavjud xatosi: {xato}")
            return False
    
    async def muddatni_ozgartirish(self, kalit: str, muddati: int) -> bool:
        """Kalitning amal qilish muddatini o'zgartiradi."""
        if self._redis is None:
            await self.ulanish()
        
        try:
            return await self._redis.expire(kalit, muddati)
        except Exception as xato:
            logger.error(f"Muddat o'zgartirish xatosi: {xato}")
            return False


# Global kesh ob'ekti
redis_kesh = RedisKesh()


def kesh_dekoratori(
    prefiks: str,
    muddati: int = None,
    kalit_funksiyasi: callable = None
):
    """
    Funksiya natijalarini keshlash uchun dekorator.
    
    Foydalanish:
        @kesh_dekoratori("foydalanuvchi", muddati=3600)
        async def foydalanuvchi_olish(id: int):
            ...
    """
    def dekorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Kalit yaratish
            if kalit_funksiyasi:
                kalit = f"{prefiks}:{kalit_funksiyasi(*args, **kwargs)}"
            else:
                kalit_qismlari = [str(arg) for arg in args]
                kalit_qismlari.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
                kalit_hash = hashlib.md5(
                    ":".join(kalit_qismlari).encode()
                ).hexdigest()[:16]
                kalit = f"{prefiks}:{kalit_hash}"
            
            # Keshdan olishga harakat
            natija = await redis_kesh.olish(kalit)
            if natija is not None:
                return natija
            
            # Funksiyani bajarish
            natija = await func(*args, **kwargs)
            
            # Natijani keshlash
            if natija is not None:
                await redis_kesh.saqlash(kalit, natija, muddati)
            
            return natija
        return wrapper
    return dekorator


# Kesh kalitlari uchun konstantalar
class KeshKalitlari:
    """Standart kesh kalit prefikslari."""
    FOYDALANUVCHI = "foydalanuvchi"
    HOLAT = "holat"
    KATEGORIYA = "kategoriya"
    STATISTIKA = "statistika"
    SESSIYA = "sessiya"
    REYTING = "reyting"
    YUTUQLAR = "yutuqlar"
