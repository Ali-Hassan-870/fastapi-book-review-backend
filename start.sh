#!/bin/sh
set -e

# Apply database migrations
alembic upgrade head

# Start the Celery worker in the background (solo pool keeps memory low on
# Render's free tier). In a production setup this would be a separate service.
celery -A src.celery_tasks worker --loglevel=info --pool=solo &

# Start the API in the foreground (PID 1 via exec so it receives signals)
exec uvicorn src:app --host 0.0.0.0 --port "${PORT:-8000}"
