#!/bin/bash
echo "Starting Celery Worker with Queue Routing..."
echo ""
echo "Make sure Redis is running on localhost:6379"
echo ""
echo "Queues: notifications, stories, cleanup, filters"
echo ""

cd "$(dirname "$0")"
source venv/bin/activate
celery -A app.celery_app worker --loglevel=info -Q notifications,stories,cleanup,filters,celery


