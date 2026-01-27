# MedCase Pro Platform - Media Servisi
# Cloudinary bilan rasm va video boshqaruvi

from typing import Optional, Dict, Any
import cloudinary
import cloudinary.uploader
import cloudinary.api
from fastapi import UploadFile
import logging

from sozlamalar.sozlamalar import sozlamalar

logger = logging.getLogger(__name__)


class MediaServisi:
    """Cloudinary orqali media boshqaruvi servisi."""
    
    def __init__(self):
        self._sozlangan = False
        self._sozlash()
    
    def _sozlash(self) -> None:
        """Cloudinary sozlamalarini o'rnatadi."""
        if not self._sozlangan:
            cloudinary.config(
                cloud_name=sozlamalar.cloudinary_cloud_nomi,
                api_key=sozlamalar.cloudinary_api_kalit,
                api_secret=sozlamalar.cloudinary_api_maxfiy,
                secure=True
            )
            self._sozlangan = True
    
    async def rasm_yuklash(
        self,
        fayl: UploadFile,
        jild: str = "medcase/rasmlar",
        transformatsiyalar: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Rasm yuklaydi."""
        try:
            # Standart transformatsiyalar
            if transformatsiyalar is None:
                transformatsiyalar = {
                    "quality": "auto:good",
                    "fetch_format": "auto"
                }
            
            # Fayl mazmunini o'qish
            mazmun = await fayl.read()
            
            # Yuklash
            natija = cloudinary.uploader.upload(
                mazmun,
                folder=jild,
                resource_type="image",
                transformation=transformatsiyalar,
                allowed_formats=["jpg", "jpeg", "png", "gif", "webp"]
            )
            
            return {
                "muvaffaqiyat": True,
                "url": natija.get("secure_url"),
                "public_id": natija.get("public_id"),
                "kenglik": natija.get("width"),
                "balandlik": natija.get("height"),
                "format": natija.get("format"),
                "hajm": natija.get("bytes")
            }
        except Exception as xato:
            logger.error(f"Rasm yuklash xatosi: {xato}")
            return {
                "muvaffaqiyat": False,
                "xato": str(xato)
            }
    
    async def video_yuklash(
        self,
        fayl: UploadFile,
        jild: str = "medcase/videolar"
    ) -> Dict[str, Any]:
        """Video yuklaydi."""
        try:
            mazmun = await fayl.read()
            
            natija = cloudinary.uploader.upload(
                mazmun,
                folder=jild,
                resource_type="video",
                allowed_formats=["mp4", "mov", "avi", "webm"]
            )
            
            return {
                "muvaffaqiyat": True,
                "url": natija.get("secure_url"),
                "public_id": natija.get("public_id"),
                "kenglik": natija.get("width"),
                "balandlik": natija.get("height"),
                "davomiylik": natija.get("duration"),
                "format": natija.get("format"),
                "hajm": natija.get("bytes")
            }
        except Exception as xato:
            logger.error(f"Video yuklash xatosi: {xato}")
            return {
                "muvaffaqiyat": False,
                "xato": str(xato)
            }
    
    async def tibbiy_rasm_yuklash(
        self,
        fayl: UploadFile,
        rasm_turi: str = "rentgen",
        jild: str = "medcase/tibbiy"
    ) -> Dict[str, Any]:
        """Tibbiy rasm yuklaydi (X-ray, CT, MRI)."""
        try:
            mazmun = await fayl.read()
            
            # Tibbiy rasmlar uchun maxsus sozlamalar
            transformatsiyalar = {
                "quality": "auto:best",
                "fetch_format": "auto"
            }
            
            # Turi bo'yicha jild
            toliq_jild = f"{jild}/{rasm_turi}"
            
            natija = cloudinary.uploader.upload(
                mazmun,
                folder=toliq_jild,
                resource_type="image",
                transformation=transformatsiyalar
            )
            
            return {
                "muvaffaqiyat": True,
                "url": natija.get("secure_url"),
                "public_id": natija.get("public_id"),
                "turi": rasm_turi,
                "kenglik": natija.get("width"),
                "balandlik": natija.get("height"),
                "hajm": natija.get("bytes")
            }
        except Exception as xato:
            logger.error(f"Tibbiy rasm yuklash xatosi: {xato}")
            return {
                "muvaffaqiyat": False,
                "xato": str(xato)
            }
    
    async def ochirish(self, public_id: str, resurs_turi: str = "image") -> bool:
        """Medianii o'chiradi."""
        try:
            natija = cloudinary.uploader.destroy(
                public_id,
                resource_type=resurs_turi
            )
            return natija.get("result") == "ok"
        except Exception as xato:
            logger.error(f"Media o'chirish xatosi: {xato}")
            return False
    
    async def jild_ochirish(self, jild: str) -> bool:
        """Jildni va barcha fayllarni o'chiradi."""
        try:
            cloudinary.api.delete_resources_by_prefix(jild)
            cloudinary.api.delete_folder(jild)
            return True
        except Exception as xato:
            logger.error(f"Jild o'chirish xatosi: {xato}")
            return False
    
    def url_yaratish(
        self,
        public_id: str,
        kenglik: int = None,
        balandlik: int = None,
        format: str = "auto"
    ) -> str:
        """Optimallashtirilgan URL yaratadi."""
        transformatsiyalar = []
        
        if kenglik or balandlik:
            trans = {}
            if kenglik:
                trans["width"] = kenglik
            if balandlik:
                trans["height"] = balandlik
            trans["crop"] = "fill"
            transformatsiyalar.append(trans)
        
        return cloudinary.CloudinaryImage(public_id).build_url(
            transformation=transformatsiyalar,
            fetch_format=format,
            quality="auto"
        )
    
    def thumbnail_url(self, public_id: str, hajm: int = 200) -> str:
        """Thumbnail URL yaratadi."""
        return self.url_yaratish(
            public_id,
            kenglik=hajm,
            balandlik=hajm
        )


# Global media servisi
media_servisi = MediaServisi()
