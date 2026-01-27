# MedCase Pro Platform - Docker Konfiguratsiyasi
# 2000-5000 concurrent users uchun optimallashtirilgan

FROM python:3.11-slim

# Muhit o'zgaruvchilari
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Ishchi katalog
WORKDIR /app

# Tizim bog'liqliklarini o'rnatish
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Python bog'liqliklarini o'rnatish
COPY talablar.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r talablar.txt

# Ilova kodini nusxalash
COPY . .

# Port
EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/sogliq || exit 1

# Ishga tushirish
CMD ["gunicorn", "ilova.asosiy:ilova", \
    "-w", "4", \
    "-k", "uvicorn.workers.UvicornWorker", \
    "-b", "0.0.0.0:8000", \
    "--timeout", "120", \
    "--keep-alive", "5", \
    "--max-requests", "1000", \
    "--max-requests-jitter", "50", \
    "--access-logfile", "-", \
    "--error-logfile", "-"]
