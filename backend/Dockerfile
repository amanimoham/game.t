# syntax=docker/dockerfile:1
FROM python:3.12-slim AS base

# --- Runtime hardening / sane defaults ---
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# System deps (build tools for argon2-cffi etc.) then clean up
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential libpq-dev curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps first (better layer caching)
COPY requirements.txt .
RUN pip install -r requirements.txt

# App source
COPY . .

# Run as non-root
RUN adduser --disabled-password --gecos "" appuser \
    && chown -R appuser:appuser /app
USER appuser

RUN chmod +x scripts/start.sh

EXPOSE 8000

CMD ["scripts/start.sh"]
