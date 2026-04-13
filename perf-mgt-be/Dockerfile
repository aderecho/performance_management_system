FROM python:3.12-slim

# -------------------------
# Environment
# -------------------------
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# -------------------------
# System dependencies
# -------------------------
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
 && rm -rf /var/lib/apt/lists/*

# -------------------------
# Non-root user
# -------------------------
RUN useradd -m appuser

# -------------------------
# Working directory
# -------------------------
WORKDIR /app

# -------------------------
# Python dependencies
# -------------------------
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# -------------------------
# App source
# -------------------------
COPY . .

# -------------------------
# Static & media dirs
# -------------------------
RUN mkdir -p /app/staticfiles /app/media \
 && chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

# -------------------------
# Default = PRODUCTION
# Dev will override this in compose
# -------------------------
CMD ["gunicorn", "perf_mgt.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]