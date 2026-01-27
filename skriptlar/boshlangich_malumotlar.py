# MedCase Pro Platform - Boshlang'ich Ma'lumotlar
# Tizimni boshlash uchun kerakli ma'lumotlar

import asyncio
from uuid import uuid4

from sqlalchemy import select, func
from sozlamalar.malumotlar_bazasi import malumotlar_bazasi, sessiya_olish
from modellar.foydalanuvchi import Foydalanuvchi, FoydalanuvchiProfili, FoydalanuvchiRoli
from modellar.kategoriya import AsosiyKategoriya, KichikKategoriya, Bolim
from modellar.gamifikatsiya import Nishon, NishonTuri, NishonNodirligi, DarajaKonfiguratsiyasi
from modellar.rivojlanish import FoydalanuvchiRivojlanishi
from yordamchilar.xavfsizlik import parol_hashlash


async def admin_yaratish(db):
    """Admin foydalanuvchi yaratish."""
    print("Admin foydalanuvchi yaratilmoqda...")
    
    # Avval mavjudligini tekshirish
    mavjud = await db.execute(
        select(Foydalanuvchi).where(Foydalanuvchi.foydalanuvchi_nomi == "admin")
    )
    admin = mavjud.scalar_one_or_none()
    
    if admin:
        print("⏭️  Admin allaqachon mavjud, o'tkazib yuborildi")
        return admin
    
    admin = Foydalanuvchi(
        email="admin@medcase.uz",
        foydalanuvchi_nomi="admin",
        parol_hash=parol_hashlash("Admin123!"),
        ism="Admin",
        familiya="MedCase Pro",
        rol=FoydalanuvchiRoli.SUPER_ADMIN,
        email_tasdiqlangan=True
    )
    db.add(admin)
    await db.flush()
    
    # Admin profili
    profil = FoydalanuvchiProfili(foydalanuvchi_id=admin.id)
    db.add(profil)
    
    # Admin rivojlanishi
    rivojlanish = FoydalanuvchiRivojlanishi(foydalanuvchi_id=admin.id)
    db.add(rivojlanish)
    
    print(f"✓ Admin yaratildi: admin@medcase.uz / Admin123!")
    return admin


async def kategoriyalar_yaratish(db):
    """Asosiy kategoriyalar yaratish."""
    print("\nKategoriyalar yaratilmoqda...")
    
    # Avval mavjudligini tekshirish
    mavjud_soni = await db.execute(select(func.count(AsosiyKategoriya.id)))
    if mavjud_soni.scalar() > 0:
        print("⏭️  Kategoriyalar allaqachon mavjud, o'tkazib yuborildi")
        return
    
    kategoriyalar = [
        {
            "nomi": "Fundamental Fanlar",
            "slug": "fundamental-fanlar",
            "tavsif": "Tibbiyotning asosiy fanlari",
            "rang": "#3B82F6",
            "tartib": 1,
            "kichik_kategoriyalar": [
                {"nomi": "Anatomiya", "slug": "anatomiya", "bolimlar": [
                    "Tana anatomiyasi", "Bosh va bo'yin", "Ko'krak qafasi", 
                    "Qorin bo'shlig'i", "Oyoq-qo'llar", "Nerv tizimi"
                ]},
                {"nomi": "Fiziologiya", "slug": "fiziologiya", "bolimlar": [
                    "Yurak-qon tomir tizimi", "Nafas olish tizimi", "Siydik-jinsiy tizim",
                    "Hazm tizimi", "Endokrin tizim", "Nerv fiziologiyasi"
                ]},
                {"nomi": "Biokimyo", "slug": "biokimyo", "bolimlar": [
                    "Oqsillar", "Karbonsuvlar", "Yog'lar", "Fermentlar", "Vitaminlar"
                ]},
                {"nomi": "Farmakologiya", "slug": "farmakologiya", "bolimlar": [
                    "Farmakokinetika", "Farmakodynamika", "Antibiotiklar",
                    "Og'riq qoldiruvchilar", "Yurak dorilar"
                ]}
            ]
        },
        {
            "nomi": "Klinik Fanlar",
            "slug": "klinik-fanlar",
            "tavsif": "Amaliy tibbiyot va ixtisosliklar",
            "rang": "#10B981",
            "tartib": 2,
            "kichik_kategoriyalar": [
                {"nomi": "Ichki kasalliklar", "slug": "ichki-kasalliklar", "bolimlar": [
                    "Kardiologiya", "Pulmonologiya", "Gastroenterologiya",
                    "Nefrologiya", "Endokrinologiya", "Revmatologiya"
                ]},
                {"nomi": "Jarrohlik", "slug": "jarrohlik", "bolimlar": [
                    "Umumiy jarrohlik", "Travmatologiya", "Neyrojarrohlik",
                    "Kardiojarrohlik", "Urolog jarrohlik"
                ]},
                {"nomi": "Pediatriya", "slug": "pediatriya", "bolimlar": [
                    "Neonatologiya", "Bolalar infektsiyalari", "Bolalar kardiologiyasi"
                ]},
                {"nomi": "Akusherlik va ginekologiya", "slug": "akusherlik-ginekologiya", "bolimlar": [
                    "Homiladorlik", "Tug'ruq", "Ginekologik kasalliklar"
                ]}
            ]
        },
        {
            "nomi": "Diagnostika",
            "slug": "diagnostika",
            "tavsif": "Diagnostika usullari va texnologiyalari",
            "rang": "#8B5CF6",
            "tartib": 3,
            "kichik_kategoriyalar": [
                {"nomi": "Radiologiya", "slug": "radiologiya", "bolimlar": [
                    "Rentgenografiya", "Kompyuter tomografiya", "MRT", "Ultratovush"
                ]},
                {"nomi": "Laboratoriya diagnostikasi", "slug": "laboratoriya", "bolimlar": [
                    "Qon tahlillari", "Siydik tahlillari", "Bioximik tahlillar"
                ]}
            ]
        }
    ]
    
    for kat_malumot in kategoriyalar:
        kategoriya = AsosiyKategoriya(
            nomi=kat_malumot["nomi"],
            slug=kat_malumot["slug"],
            tavsif=kat_malumot["tavsif"],
            rang=kat_malumot["rang"],
            tartib=kat_malumot["tartib"]
        )
        db.add(kategoriya)
        await db.flush()
        
        for kichik_malumot in kat_malumot["kichik_kategoriyalar"]:
            kichik = KichikKategoriya(
                asosiy_kategoriya_id=kategoriya.id,
                nomi=kichik_malumot["nomi"],
                slug=kichik_malumot["slug"],
                tartib=0
            )
            db.add(kichik)
            await db.flush()
            
            for i, bolim_nomi in enumerate(kichik_malumot["bolimlar"]):
                bolim = Bolim(
                    kichik_kategoriya_id=kichik.id,
                    nomi=bolim_nomi,
                    slug=bolim_nomi.lower().replace(" ", "-").replace("'", ""),
                    tartib=i
                )
                db.add(bolim)
        
        print(f"✓ {kat_malumot['nomi']} kategoriyasi yaratildi")
    
    await db.flush()


async def nishonlar_yaratish(db):
    """Nishonlar yaratish."""
    print("\nNishonlar yaratilmoqda...")
    
    # Avval mavjudligini tekshirish
    mavjud_soni = await db.execute(select(func.count(Nishon.id)))
    if mavjud_soni.scalar() > 0:
        print("⏭️  Nishonlar allaqachon mavjud, o'tkazib yuborildi")
        return
    
    nishonlar = [
        # Bosqich nishonlari
        {"nom": "Birinchi qadam", "kod": "first_step", "tavsif": "Birinchi holatni yeching",
         "turi": NishonTuri.BOSQICH, "nodirlik": NishonNodirligi.ODDIY, "ball": 10,
         "shartlar": {"turi": "holatlar_soni", "qiymat": 1}},
        {"nom": "O'n qahramon", "kod": "ten_hero", "tavsif": "10 ta holatni yeching",
         "turi": NishonTuri.BOSQICH, "nodirlik": NishonNodirligi.ODDIY, "ball": 50,
         "shartlar": {"turi": "holatlar_soni", "qiymat": 10}},
        {"nom": "Yuz ustasi", "kod": "hundred_master", "tavsif": "100 ta holatni yeching",
         "turi": NishonTuri.BOSQICH, "nodirlik": NishonNodirligi.NODIR, "ball": 200,
         "shartlar": {"turi": "holatlar_soni", "qiymat": 100}},
        {"nom": "Ming ustasi", "kod": "thousand_master", "tavsif": "1000 ta holatni yeching",
         "turi": NishonTuri.BOSQICH, "nodirlik": NishonNodirligi.EPIK, "ball": 1000,
         "shartlar": {"turi": "holatlar_soni", "qiymat": 1000}},
        
        # Streak nishonlari
        {"nom": "Bir haftalik", "kod": "week_streak", "tavsif": "7 kun ketma-ket o'qing",
         "turi": NishonTuri.STREAK, "nodirlik": NishonNodirligi.ODDIY, "ball": 70,
         "shartlar": {"turi": "streak", "qiymat": 7}},
        {"nom": "Oylik chempion", "kod": "month_streak", "tavsif": "30 kun ketma-ket o'qing",
         "turi": NishonTuri.STREAK, "nodirlik": NishonNodirligi.NODIR, "ball": 300,
         "shartlar": {"turi": "streak", "qiymat": 30}},
        {"nom": "Yuz kunlik", "kod": "hundred_streak", "tavsif": "100 kun ketma-ket o'qing",
         "turi": NishonTuri.STREAK, "nodirlik": NishonNodirligi.AFSONAVIY, "ball": 1000,
         "shartlar": {"turi": "streak", "qiymat": 100}},
        
        # Aniqlik nishonlari
        {"nom": "Aniq nishonchi", "kod": "accurate_90", "tavsif": "90% aniqlikka erishing",
         "turi": NishonTuri.ANIQLIK, "nodirlik": NishonNodirligi.NODIR, "ball": 200,
         "shartlar": {"turi": "aniqlik", "qiymat": 90}},
        {"nom": "Mukammal", "kod": "perfect_95", "tavsif": "95% aniqlikka erishing",
         "turi": NishonTuri.ANIQLIK, "nodirlik": NishonNodirligi.EPIK, "ball": 500,
         "shartlar": {"turi": "aniqlik", "qiymat": 95}},
    ]
    
    for n in nishonlar:
        nishon = Nishon(
            nom=n["nom"],
            kod=n["kod"],
            tavsif=n["tavsif"],
            turi=n["turi"],
            nodirlik=n["nodirlik"],
            ball_qiymati=n["ball"],
            ochish_shartlari=n["shartlar"]
        )
        db.add(nishon)
    
    await db.flush()
    print(f"✓ {len(nishonlar)} ta nishon yaratildi")


async def darajalar_yaratish(db):
    """Daraja konfiguratsiyasini yaratish."""
    print("\nDarajalar yaratilmoqda...")
    
    # Avval mavjudligini tekshirish
    mavjud_soni = await db.execute(select(func.count(DarajaKonfiguratsiyasi.id)))
    if mavjud_soni.scalar() > 0:
        print("⏭️  Darajalar allaqachon mavjud, o'tkazib yuborildi")
        return
    
    darajalar = [
        {"daraja": 1, "nom": "Yangi boshlovchi", "ball": 0, "rang": "#9CA3AF"},
        {"daraja": 2, "nom": "O'rganuvchi", "ball": 100, "rang": "#6B7280"},
        {"daraja": 3, "nom": "Talaba", "ball": 300, "rang": "#3B82F6"},
        {"daraja": 4, "nom": "Ilg'or talaba", "ball": 600, "rang": "#2563EB"},
        {"daraja": 5, "nom": "Bilimdon", "ball": 1000, "rang": "#10B981"},
        {"daraja": 6, "nom": "Mohir", "ball": 1500, "rang": "#059669"},
        {"daraja": 7, "nom": "Mutaxassis", "ball": 2200, "rang": "#8B5CF6"},
        {"daraja": 8, "nom": "Ekspert", "ball": 3000, "rang": "#7C3AED"},
        {"daraja": 9, "nom": "Usta", "ball": 4000, "rang": "#F59E0B"},
        {"daraja": 10, "nom": "Grandmaster", "ball": 5000, "rang": "#D97706"},
        {"daraja": 11, "nom": "Shifokor", "ball": 6500, "rang": "#EF4444"},
        {"daraja": 12, "nom": "Professor", "ball": 8000, "rang": "#DC2626"},
        {"daraja": 13, "nom": "Akademik", "ball": 10000, "rang": "#B91C1C"},
        {"daraja": 14, "nom": "Legenda", "ball": 12500, "rang": "#FFD700"},
        {"daraja": 15, "nom": "Buyuk Tabib", "ball": 15000, "rang": "#FFD700"},
    ]
    
    for d in darajalar:
        daraja = DarajaKonfiguratsiyasi(
            daraja=d["daraja"],
            nom=d["nom"],
            kerakli_ball=d["ball"],
            rang=d["rang"]
        )
        db.add(daraja)
    
    await db.flush()
    print(f"✓ {len(darajalar)} ta daraja yaratildi")


async def asosiy():
    """Asosiy funksiya."""
    print("=" * 50)
    print("MedCase Pro Platform - Boshlang'ich Ma'lumotlar")
    print("=" * 50)
    
    await malumotlar_bazasi.ulanish()
    
    async with malumotlar_bazasi.sessiya() as db:
        try:
            await admin_yaratish(db)
            await kategoriyalar_yaratish(db)
            await nishonlar_yaratish(db)
            await darajalar_yaratish(db)
            
            await db.commit()
            print("\n" + "=" * 50)
            print("✅ Barcha ma'lumotlar muvaffaqiyatli yaratildi!")
            print("=" * 50)
        except Exception as e:
            await db.rollback()
            print(f"\n❌ Xato yuz berdi: {e}")
            raise
    
    await malumotlar_bazasi.uzish()


if __name__ == "__main__":
    asyncio.run(asosiy())
