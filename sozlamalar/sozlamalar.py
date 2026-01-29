# MedCase Pro Platform - Asosiy Sozlamalar
# Barcha muhit o'zgaruvchilari va konfiguratsiyalar

from pydantic_settings import BaseSettings
from pydantic import Field, field_validator
from typing import List, Optional
from functools import lru_cache
import os


class Sozlamalar(BaseSettings):
    """
    MedCase Pro platformasi uchun asosiy sozlamalar.
    Barcha muhit o'zgaruvchilari bu yerda boshqariladi.
    """
    
    # =====================================================
    # ILOVA SOZLAMALARI
    # =====================================================
    ilova_nomi: str = Field(default="MedCase Pro", alias="ILOVA_NOMI")
    ilova_versiyasi: str = Field(default="1.0.0", alias="ILOVA_VERSIYASI")
    muhit: str = Field(default="ishlab_chiqish", alias="MUHIT")
    debug: bool = Field(default=True, alias="DEBUG")
    maxfiy_kalit: str = Field(
        default="standart_maxfiy_kalit_ishlab_chiqarishda_ozgartiring",
        alias="MAXFIY_KALIT"
    )
    
    # =====================================================
    # MA'LUMOTLAR BAZASI
    # =====================================================
    malumotlar_bazasi_url: str = Field(
        default="postgresql+asyncpg://localhost/medcase",
        alias="MALUMOTLAR_BAZASI_URL"
    )
    
    # =====================================================
    # REDIS
    # =====================================================
    redis_url: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")
    redis_parol: Optional[str] = Field(default=None, alias="REDIS_PAROL")
    kesh_ttl: int = Field(default=3600, alias="KESH_TTL")
    
    # =====================================================
    # JWT AUTENTIFIKATSIYA
    # =====================================================
    jwt_maxfiy_kalit: str = Field(
        default="jwt_standart_maxfiy_kalit",
        alias="JWT_MAXFIY_KALIT"
    )
    jwt_algoritm: str = Field(default="HS256", alias="JWT_ALGORITM")
    kirish_token_muddati: int = Field(default=30, alias="KIRISH_TOKEN_MUDDATI")  # daqiqalar
    yangilash_token_muddati: int = Field(default=10080, alias="YANGILASH_TOKEN_MUDDATI")  # daqiqalar
    
    # =====================================================
    # CLOUDINARY
    # =====================================================
    cloudinary_cloud_nomi: str = Field(default="", alias="CLOUDINARY_CLOUD_NOMI")
    cloudinary_api_kalit: str = Field(default="", alias="CLOUDINARY_API_KALIT")
    cloudinary_api_maxfiy: str = Field(default="", alias="CLOUDINARY_API_MAXFIY")
    
    # =====================================================
    # EMAIL
    # =====================================================
    smtp_host: str = Field(default="smtp.gmail.com", alias="SMTP_HOST")
    smtp_port: int = Field(default=587, alias="SMTP_PORT")
    smtp_foydalanuvchi: Optional[str] = Field(default=None, alias="SMTP_FOYDALANUVCHI")
    smtp_parol: Optional[str] = Field(default=None, alias="SMTP_PAROL")
    email_yuboruvchi: str = Field(default="noreply@medcase.uz", alias="EMAIL_YUBORUVCHI")
    
    # =====================================================
    # OAUTH
    # =====================================================
    google_client_id: Optional[str] = Field(default=None, alias="GOOGLE_CLIENT_ID")
    google_client_secret: Optional[str] = Field(default=None, alias="GOOGLE_CLIENT_SECRET")
    microsoft_client_id: Optional[str] = Field(default=None, alias="MICROSOFT_CLIENT_ID")
    microsoft_client_secret: Optional[str] = Field(default=None, alias="MICROSOFT_CLIENT_SECRET")
    
    # =====================================================
    # RATE LIMITING
    # =====================================================
    rate_limit_enabled: bool = Field(default=False, alias="RATE_LIMIT_ENABLED")
    rate_limit_per_minute: int = Field(default=60, alias="RATE_LIMIT_PER_MINUTE")
    rate_limit_per_hour: int = Field(default=1000, alias="RATE_LIMIT_PER_HOUR")
    abuse_block_enabled: bool = Field(default=True, alias="ABUSE_BLOCK_ENABLED")
    abuse_block_threshold: int = Field(default=1000, alias="ABUSE_BLOCK_THRESHOLD")
    abuse_block_window_seconds: int = Field(default=3600, alias="ABUSE_BLOCK_WINDOW_SECONDS")
    abuse_block_duration_seconds: int = Field(default=36000, alias="ABUSE_BLOCK_DURATION_SECONDS")
    
    # =====================================================
    # CORS
    # =====================================================
    ruxsat_berilgan_manbalar: str = Field(
        default="http://localhost:3000,http://localhost:8080",
        alias="RUXSAT_BERILGAN_MANBALAR"
    )
    ruxsat_berilgan_metodlar: str = Field(
        default="GET,POST,PUT,DELETE,PATCH",
        alias="RUXSAT_BERILGAN_METODLAR"
    )
    ruxsat_berilgan_sarlavhalar: str = Field(default="*", alias="RUXSAT_BERILGAN_SARLAVHALAR")
    
    # =====================================================
    # LOGGING
    # =====================================================
    log_darajasi: str = Field(default="INFO", alias="LOG_DARAJASI")
    log_formati: str = Field(default="json", alias="LOG_FORMATI")

    # =====================================================
    # WEB PUSH (VAPID)
    # =====================================================
    vapid_public_key: Optional[str] = Field(default=None, alias="VAPID_PUBLIC_KEY")
    vapid_private_key: Optional[str] = Field(default=None, alias="VAPID_PRIVATE_KEY")
    vapid_subject: str = Field(default="mailto:admin@medcasepro.uz", alias="VAPID_SUBJECT")
    
    # =====================================================
    # SENTRY
    # =====================================================
    sentry_dsn: Optional[str] = Field(default=None, alias="SENTRY_DSN")
    
    # =====================================================
    # PAGINATION
    # =====================================================
    standart_sahifa_hajmi: int = Field(default=20, alias="STANDART_SAHIFA_HAJMI")
    maksimal_sahifa_hajmi: int = Field(default=100, alias="MAKSIMAL_SAHIFA_HAJMI")
    
    @property
    def cors_manbalar_royxati(self) -> List[str]:
        """CORS manbalarini ro'yxat sifatida qaytaradi."""
        return [manba.strip() for manba in self.ruxsat_berilgan_manbalar.split(",")]
    
    @property
    def cors_metodlar_royxati(self) -> List[str]:
        """CORS metodlarini ro'yxat sifatida qaytaradi."""
        return [metod.strip() for metod in self.ruxsat_berilgan_metodlar.split(",")]
    
    @property
    def cors_sarlavhalar_royxati(self) -> List[str]:
        """CORS sarlavhalarini ro'yxat sifatida qaytaradi."""
        if self.ruxsat_berilgan_sarlavhalar == "*":
            return ["*"]
        return [sarlavha.strip() for sarlavha in self.ruxsat_berilgan_sarlavhalar.split(",")]
    
    @property
    def ishlab_chiqarish_muhiti(self) -> bool:
        """Ishlab chiqarish muhitida ekanligini tekshiradi."""
        return self.muhit == "ishlab_chiqarish"
    
    @property
    def sinov_muhiti(self) -> bool:
        """Sinov muhitida ekanligini tekshiradi."""
        return self.muhit == "sinov"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"


@lru_cache()
def sozlamalar_olish() -> Sozlamalar:
    """
    Sozlamalar ob'ektini yaratadi va keshlaydi.
    Singleton pattern - faqat bir marta yaratiladi.
    """
    return Sozlamalar()


# Global sozlamalar ob'ekti
sozlamalar = sozlamalar_olish()
