#!/bin/bash
# MedCase Pro Platform - Ishlab chiqarish uchun ishga tushirish

set -e

echo "================================================"
echo "MedCase Pro Platform - Ishlab Chiqarish"
echo "================================================"

# Muhit tekshirish
export MUHIT=ishlab_chiqarish
export DEBUG=False

# Migratsiya
echo "Ma'lumotlar bazasi migratsiyasi tekshirilmoqda..."
if python -m skriptlar.migratsiya_tekshirish 2>/dev/null; then
    echo "✅ Migratsiyalar allaqachon qo'llangan, qayta ishlamaydi"
else
    echo "Ma'lumotlar bazasi migratsiyasi ishga tushirilmoqda..."
    alembic upgrade head
fi

# Gunicorn bilan ishga tushirish
echo "Server ishga tushmoqda (Gunicorn)..."
gunicorn ilova.asosiy:ilova \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000 \
    --timeout 120 \
    --keep-alive 5 \
    --max-requests 1000 \
    --max-requests-jitter 50 \
    --access-logfile - \
    --error-logfile - \
    --capture-output \
    --enable-stdio-inheritance
