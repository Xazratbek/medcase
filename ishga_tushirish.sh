#!/bin/bash
# MedCase Pro Platform - Ishga tushirish skripti

set -e

echo "================================================"
echo "MedCase Pro Platform - Ishga Tushirish"
echo "================================================"

# Virtual muhit tekshirish
if [ ! -d "venv" ]; then
    echo "Virtual muhit yaratilmoqda..."
    python3 -m venv venv
fi

# Virtual muhitni faollashtirish
source venv/bin/activate

# Bog'liqliklarni o'rnatish
echo "Bog'liqliklar o'rnatilmoqda..."
pip install -r talablar.txt

# Muhit o'zgaruvchilarini tekshirish
if [ ! -f ".env" ]; then
    echo "⚠️  .env fayli topilmadi!"
    echo ".env.namuna dan nusxa oling va sozlang."
    exit 1
fi

# Ma'lumotlar bazasi migratsiyasi
echo "Ma'lumotlar bazasi migratsiyasi tekshirilmoqda..."
if python -m skriptlar.migratsiya_tekshirish 2>/dev/null; then
    echo "✅ Migratsiyalar allaqachon qo'llangan, qayta ishlamaydi"
else
    echo "Ma'lumotlar bazasi migratsiyasi ishga tushirilmoqda..."
    alembic upgrade head || echo "⚠️  Migratsiya xatosi (jadvallar mavjud bo'lishi mumkin)"
fi

# Boshlang'ich ma'lumotlar
echo "Boshlang'ich ma'lumotlar yuklanmoqda..."
python -m skriptlar.boshlangich_malumotlar || echo "Ma'lumotlar allaqachon mavjud"

# Serverni ishga tushirish
echo ""
echo "================================================"
echo "Server ishga tushmoqda..."
echo "API: http://localhost:8000"
echo "Hujjatlar: http://localhost:8000/hujjatlar"
echo "================================================"

uvicorn ilova.asosiy:ilova --host 0.0.0.0 --port 8000 --reload
