FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY alembic.ini .
COPY migrations ./migrations
COPY src ./src
COPY start.sh .

EXPOSE 8000

# start.sh runs migrations, launches the Celery worker in the background,
# then starts uvicorn on ${PORT} (injected by Render)
CMD ["sh", "start.sh"]
