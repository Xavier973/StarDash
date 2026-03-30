FROM python:3.10-slim

WORKDIR /app

# Dépendances système (psycopg2-binary n'en a pas besoin, mais utile pour debug)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY dashboard/ ./dashboard/
COPY etl/       ./etl/
COPY run_etl.py .
COPY .env       .env

ENV PYTHONUNBUFFERED=1

WORKDIR /app/dashboard

EXPOSE 8050

CMD ["python", "app.py"]
