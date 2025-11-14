@echo off
echo Starting Celery Worker with Queue Routing...
echo.
echo Make sure Redis is running on localhost:6379
echo.
echo Queues: notifications, stories, cleanup, filters
echo.

cd /d "%~dp0"
call venv\Scripts\activate.bat
celery -A app.celery_app worker --loglevel=info --pool=solo -Q notifications,stories,cleanup,filters,celery

pause


