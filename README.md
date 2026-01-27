# 🏥 MedCase Pro Platform

## Tibbiyot Talabalari va Shifokorlar uchun Interaktiv Ta'lim Platformasi

MedCase Pro - tibbiyot talabalari va amaliyotchi shifokorlar uchun mo'ljallangan interaktiv tibbiy ta'lim platformasi. Platforma real klinik holatlar asosida o'qitish orqali klinik fikrlash ko'nikmalarini rivojlantirishga yordam beradi.

---

## 📋 Xususiyatlar

### 🔐 Autentifikatsiya va Foydalanuvchi Boshqaruvi
- Ko'p rollli tizim (Talaba, Rezident, Shifokor, O'qituvchi, Admin)
- JWT asosidagi xavfsiz autentifikatsiya
- OAuth integratsiyasi (Google, Microsoft)
- Ko'p qurilmadan sessiya boshqaruvi

### 📚 Kontent Tashkiloti
- Uch bosqichli taksonomiya (Kategoriya → Kichik kategoriya → Bo'lim)
- Fundamental fanlar, Klinik fanlar, Diagnostika

### 🎯 Holatga Asoslangan O'qitish
- Klinik stsenariylar va MCQ savollar
- Video va rasm qo'llab-quvvatlash (Cloudinary)
- Batafsil tushuntirishlar
- Qiyinlik darajalari (Oson, O'rtacha, Qiyin)

### 📊 Rivojlanish Kuzatuvi
- Shaxsiy statistika va analitika
- Kunlik, haftalik, oylik hisobotlar
- Streak (ketma-ket kunlar) kuzatuvi
- Kuchli va zaif tomonlar tahlili

### 🏆 Gamifikatsiya
- Ball va daraja tizimi (15 ta daraja)
- Nishonlar va yutuqlar
- Global va kategoriya bo'yicha reytinglar

### 🔔 Bildirishnomalar
- Ilova ichidagi bildirishnomalar
- Streak eslatmalari
- Yangi yutuq xabarlari

---

## 🛠 Texnologiyalar

| Komponent | Texnologiya |
|-----------|-------------|
| Backend | FastAPI (Python 3.11+) |
| Ma'lumotlar bazasi | PostgreSQL (Neon) |
| Cache | Redis |
| Media saqlash | Cloudinary |
| Autentifikatsiya | JWT (python-jose) |
| ORM | SQLAlchemy 2.0 (Async) |
| Migratsiya | Alembic |
| Konteyner | Docker |
| Web Server | Nginx + Gunicorn |

---

## 📁 Loyiha Strukturasi

```
medcase/
├── ilova/                      # Asosiy FastAPI ilovasi
│   ├── asosiy.py              # Ilova yaratish va sozlash
│   └── __init__.py
├── sozlamalar/                 # Konfiguratsiya
│   ├── sozlamalar.py          # Muhit o'zgaruvchilari
│   ├── malumotlar_bazasi.py   # PostgreSQL ulanishi
│   ├── redis_kesh.py          # Redis keshlash
│   └── __init__.py
├── modellar/                   # SQLAlchemy modellari
│   ├── asosiy.py              # Bazaviy model
│   ├── foydalanuvchi.py       # Foydalanuvchi modellari
│   ├── kategoriya.py          # Kategoriya modellari
│   ├── holat.py               # Klinik holat modellari
│   ├── rivojlanish.py         # Rivojlanish kuzatuvi
│   ├── gamifikatsiya.py       # Nishonlar va ballar
│   ├── xatcho.py              # Xatcholar va eslatmalar
│   ├── obuna.py               # Obuna va to'lovlar
│   ├── bildirishnoma.py       # Bildirishnomalar
│   └── __init__.py
├── sxemalar/                   # Pydantic sxemalari
│   ├── asosiy.py              # Umumiy sxemalar
│   ├── foydalanuvchi.py       # Foydalanuvchi sxemalari
│   ├── kategoriya.py          # Kategoriya sxemalari
│   ├── holat.py               # Holat sxemalari
│   ├── rivojlanish.py         # Rivojlanish sxemalari
│   ├── gamifikatsiya.py       # Gamifikatsiya sxemalari
│   └── __init__.py
├── servislar/                  # Biznes mantiq
│   ├── asosiy_servis.py       # CRUD bazaviy servis
│   ├── foydalanuvchi_servisi.py
│   ├── autentifikatsiya_servisi.py
│   ├── kategoriya_servisi.py
│   ├── holat_servisi.py
│   ├── rivojlanish_servisi.py
│   ├── gamifikatsiya_servisi.py
│   ├── media_servisi.py       # Cloudinary integratsiyasi
│   ├── bildirishnoma_servisi.py
│   └── __init__.py
├── marshrutlar/                # API endpointlari
│   ├── autentifikatsiya.py    # /api/v1/autentifikatsiya
│   ├── foydalanuvchi.py       # /api/v1/foydalanuvchi
│   ├── kategoriya.py          # /api/v1/kategoriya
│   ├── holat.py               # /api/v1/holat
│   ├── rivojlanish.py         # /api/v1/rivojlanish
│   ├── gamifikatsiya.py       # /api/v1/gamifikatsiya
│   ├── bildirishnoma.py       # /api/v1/bildirishnoma
│   ├── admin.py               # /api/v1/admin
│   └── __init__.py
├── middleware/                 # Middleware qatlami
│   ├── autentifikatsiya.py    # JWT tekshirish
│   ├── rate_limiter.py        # So'rovlar cheklash
│   └── __init__.py
├── yordamchilar/              # Helper funksiyalar
│   ├── xavfsizlik.py          # Parol, JWT
│   └── __init__.py
├── vositalar/                  # Utility funksiyalar
│   ├── umumiy.py              # Umumiy funksiyalar
│   └── __init__.py
├── migratsiyalar/             # Alembic migratsiyalari
│   ├── env.py
│   ├── script.py.mako
│   └── versiyalar/
├── testlar/                    # Testlar
│   ├── conftest.py            # Test konfiguratsiyasi
│   ├── test_autentifikatsiya.py
│   ├── test_holatlar.py
│   └── __init__.py
├── skriptlar/                  # Yordamchi skriptlar
│   ├── boshlangich_malumotlar.py
│   └── __init__.py
├── .env                        # Muhit o'zgaruvchilari
├── .env.namuna                 # Namuna konfiguratsiya
├── .gitignore
├── talablar.txt               # Python bog'liqliklari
├── alembic.ini                # Alembic konfiguratsiyasi
├── Dockerfile                 # Docker image
├── docker-compose.yml         # Docker Compose
├── nginx.conf                 # Nginx konfiguratsiyasi
├── ishga_tushirish.sh         # Ishlab chiqish uchun
├── ishlab_chiqarish.sh        # Production uchun
└── README.md
```

---

## 🚀 O'rnatish va Ishga Tushirish

### ⚠️ Muhim: Python Versiyasi

> **Python 3.10, 3.11 yoki 3.12** tavsiya etiladi.
> Python 3.14 hali juda yangi va ko'p kutubxonalar (`asyncpg`, `pydantic-core`, `psycopg2`) qo'llab-quvvatlanmagan.

### 1. Loyihani klonlash
```bash
git clone https://github.com/medcase/platform.git
cd medcase
```

### 2. Virtual muhit yaratish

#### Mac (Homebrew bilan)
```bash
# Agar Python 3.14 ishlatayotgan bo'lsangiz, Python 3.12 o'rnating
brew install python@3.12

# Virtual muhit yaratish
python3.12 -m venv venv
source venv/bin/activate
```

#### Linux
```bash
python3 -m venv venv
source venv/bin/activate
```

#### Windows
```bash
python -m venv venv
.\venv\Scripts\activate
```

### 3. Bog'liqliklarni o'rnatish
```bash
pip install --upgrade pip
pip install -r talablar.txt
```

### 4. Muhit o'zgaruvchilarini sozlash
```bash
cp .env.namuna .env
# .env faylini tahrirlang
```

### 5. Ma'lumotlar bazasi migratsiyasi
```bash
alembic upgrade head
```

### 6. Boshlang'ich ma'lumotlarni yuklash
```bash
python -m skriptlar.boshlangich_malumotlar
```

### 7. Serverni ishga tushirish
```bash
# Ishlab chiqish
uvicorn ilova.asosiy:ilova --reload

# yoki skript bilan
./ishga_tushirish.sh
```

### Docker bilan ishga tushirish

#### Neon PostgreSQL bilan (tavsiya etiladi)
```bash
# .env faylida MALUMOTLAR_BAZASI_URL to'g'ri ekanligini tekshiring
docker-compose up -d
```

#### Lokal PostgreSQL bilan
```bash
# Lokal PostgreSQL va Redis ham ishga tushadi
docker-compose --profile lokal up -d
```

#### 🍎 Mac'da muammolar bo'lsa
Agar Python 3.14 bilan kutubxonalar o'rnatilmasa, Docker eng oson yechim:
```bash
docker-compose up --build -d
```
Docker Python 3.11 ishlatadi va barcha bog'liqliklar to'g'ri o'rnatiladi.

---

## 📡 API Endpointlari

Server ishga tushgandan so'ng:
- **API**: http://localhost:8000
- **Swagger UI**: http://localhost:8000/hujjatlar
- **ReDoc**: http://localhost:8000/qayta-hujjatlar

### Asosiy Endpointlar

| Yo'l | Tavsif |
|------|--------|
| `POST /api/v1/autentifikatsiya/royxatdan-otish` | Ro'yxatdan o'tish |
| `POST /api/v1/autentifikatsiya/kirish` | Tizimga kirish |
| `GET /api/v1/kategoriya/` | Kategoriyalar ro'yxati |
| `GET /api/v1/holat/` | Holatlar ro'yxati |
| `POST /api/v1/holat/{id}/javob` | Holatga javob berish |
| `GET /api/v1/rivojlanish/` | Rivojlanish statistikasi |
| `GET /api/v1/gamifikatsiya/reyting` | Reyting jadvali |

---

## ⚡ Performance (2000-5000 Concurrent Users)

### Optimizatsiyalar:
- **Connection Pooling**: SQLAlchemy async pool (20-50 connections)
- **Redis Caching**: Tez-tez so'raladigan ma'lumotlar keshlash
- **Rate Limiting**: So'rovlar sonini cheklash
- **Gzip Compression**: Javoblarni siqish
- **Database Indexing**: Optimallashtirilgan indekslar
- **Nginx Load Balancing**: Yukni taqsimlash

### Tavsiya etilgan server konfiguratsiyasi:
- **CPU**: 4+ cores
- **RAM**: 8+ GB
- **PostgreSQL**: Dedicated instance yoki Neon
- **Redis**: 512 MB+ cache

---

## 🧪 Testlarni Ishga Tushirish

```bash
# Barcha testlar
pytest

# Coverage bilan
pytest --cov=. --cov-report=html

# Ma'lum test
pytest testlar/test_autentifikatsiya.py -v
```

---

## 📦 Production Deployment

### 1. Docker bilan
```bash
docker build -t medcase:latest .
docker run -d -p 8000:8000 --env-file .env medcase:latest
```

### 2. Docker Compose bilan
```bash
docker-compose --profile ishlab_chiqarish up -d
```

### 3. Gunicorn bilan
```bash
./ishlab_chiqarish.sh
```

---

## 🔒 Xavfsizlik

- HTTPS/SSL shifrlash
- JWT token autentifikatsiya
- Bcrypt parol hashlash
- Rate limiting
- CORS konfiguratsiyasi
- SQL injection himoyasi
- XSS himoyasi

---

## 📝 Litsenziya

Barcha huquqlar himoyalangan © 2024 MedCase Pro

---

## 👥 Jamoa

MedCase Pro jamoasi tomonidan ishlab chiqilgan.

**Aloqa**: info@medcase.uz
# medcasepro
