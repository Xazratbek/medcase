# MedCase Pro Platform - Pydantic Sxemalar
# API uchun kirish/chiqish sxemalari

from sxemalar.asosiy import (
    AsosiySchema,
    SahifalashSchema,
    SahifalanganJavob,
    MuvaffaqiyatJavob,
    XatoJavob
)
from sxemalar.foydalanuvchi import (
    FoydalanuvchiYaratish,
    FoydalanuvchiKirish,
    FoydalanuvchiJavob,
    FoydalanuvchiYangilash,
    ProfilYangilash,
    ProfilJavob,
    TokenJavob,
    TokenYangilash,
    ParolOzgartirish,
    EmailTasdiqlash
)
from sxemalar.kategoriya import (
    AsosiyKategoriyaYaratish,
    AsosiyKategoriyaJavob,
    KichikKategoriyaYaratish,
    KichikKategoriyaJavob,
    BolimYaratish,
    BolimJavob,
    KategoriyalarRoyxati
)
from sxemalar.holat import (
    HolatYaratish,
    HolatJavob,
    HolatYangilash,
    HolatQidirish,
    VariantYaratish,
    MediaYaratish,
    HolatRoyxati
)
from sxemalar.rivojlanish import (
    UrinishYaratish,
    UrinishJavob,
    StatistikaJavob,
    KunlikStatistikaJavob,
    RivojlanishJavob,
    BolimRivojlanishiJavob
)
from sxemalar.gamifikatsiya import (
    NishonJavob,
    FoydalanuvchiNishoniJavob,
    BallJavob,
    ReytingJavob,
    DarajaJavob
)

__all__ = [
    # Asosiy
    "AsosiySchema",
    "SahifalashSchema",
    "SahifalanganJavob",
    "MuvaffaqiyatJavob",
    "XatoJavob",
    # Foydalanuvchi
    "FoydalanuvchiYaratish",
    "FoydalanuvchiKirish",
    "FoydalanuvchiJavob",
    "FoydalanuvchiYangilash",
    "ProfilYangilash",
    "ProfilJavob",
    "TokenJavob",
    "TokenYangilash",
    "ParolOzgartirish",
    "EmailTasdiqlash",
    # Kategoriya
    "AsosiyKategoriyaYaratish",
    "AsosiyKategoriyaJavob",
    "KichikKategoriyaYaratish",
    "KichikKategoriyaJavob",
    "BolimYaratish",
    "BolimJavob",
    "KategoriyalarRoyxati",
    # Holat
    "HolatYaratish",
    "HolatJavob",
    "HolatYangilash",
    "HolatQidirish",
    "VariantYaratish",
    "MediaYaratish",
    "HolatRoyxati",
    # Rivojlanish
    "UrinishYaratish",
    "UrinishJavob",
    "StatistikaJavob",
    "KunlikStatistikaJavob",
    "RivojlanishJavob",
    "BolimRivojlanishiJavob",
    # Gamifikatsiya
    "NishonJavob",
    "FoydalanuvchiNishoniJavob",
    "BallJavob",
    "ReytingJavob",
    "DarajaJavob",
]
