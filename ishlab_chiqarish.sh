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

# Gunicorn sozlamalari (CPU asosida)
CPU_CORES=$(nproc 2>/dev/null || echo 2)
DEFAULT_WORKERS=$((CPU_CORES * 2))

GUNICORN_WORKERS=${GUNICORN_WORKERS:-$DEFAULT_WORKERS}
GUNICORN_THREADS=${GUNICORN_THREADS:-2}
GUNICORN_TIMEOUT=${GUNICORN_TIMEOUT:-120}
GUNICORN_KEEPALIVE=${GUNICORN_KEEPALIVE:-5}
GUNICORN_MAX_REQUESTS=${GUNICORN_MAX_REQUESTS:-1000}
GUNICORN_MAX_REQUESTS_JITTER=${GUNICORN_MAX_REQUESTS_JITTER:-50}

# Gunicorn bilan ishga tushirish
echo "Server ishga tushmoqda (Gunicorn)..."
echo "Workers: $GUNICORN_WORKERS, Threads: $GUNICORN_THREADS"
gunicorn ilova.asosiy:ilova \
    --workers "$GUNICORN_WORKERS" \
    --threads "$GUNICORN_THREADS" \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000 \
    --timeout "$GUNICORN_TIMEOUT" \
    --keep-alive "$GUNICORN_KEEPALIVE" \
    --max-requests "$GUNICORN_MAX_REQUESTS" \
    --max-requests-jitter "$GUNICORN_MAX_REQUESTS_JITTER" \
    --access-logfile - \
    --error-logfile - \
    --capture-output \
    --enable-stdio-inheritance
