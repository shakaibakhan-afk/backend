#!/bin/bash
echo "Starting Celery Beat (Scheduler)..."
echo ""
echo "Make sure Redis is running on localhost:6379"
echo ""

cd "$(dirname "$0")/.."
source venv/bin/activate
celery -A app.celery_app beat --loglevel=info



