# -------- Стадия 1: Сборка зависимостей --------
FROM python:3.11-slim AS builder

WORKDIR /app

# Устанавливаем системные библиотеки, нужные для сборки
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libjpeg-dev \
    libxml2-dev \
    libxslt1-dev \
    git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY app/requirements.txt .

# Устанавливаем зависимости во временную директорию
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir --prefix=/install -r requirements.txt

# -------- Стадия 2: Финальный минимальный образ --------
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1
WORKDIR /app

# Устанавливаем системные библиотеки для запуска (без компиляции)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libjpeg-dev \
    libxml2 \
    libxslt1.1 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Копируем установленные пакеты с предыдущего слоя
COPY --from=builder /install /usr/local

# Копируем исходный код
COPY app ./app

# Команда запуска
CMD ["python", "app/main.py"]
