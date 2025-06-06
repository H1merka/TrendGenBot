# Official Python 3.11
FROM python:3.11-slim

# Installing system dependencies for the build
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    libffi-dev \
    libpq-dev \
    libssl-dev \
    libjpeg-dev \
    libxml2-dev \
    libxslt1-dev \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

# Installing dependencies without a cache for a smaller size
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

CMD ["python", "app/bot.py"]
