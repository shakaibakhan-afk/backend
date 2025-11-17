@echo off
echo Starting Celery Beat (Scheduler)...
echo.
echo Make sure Redis is running on localhost:6379
echo.

cd /d "%~dp0\.."
call venv\Scripts\activate.bat
celery -A app.celery_app beat --loglevel=info

pause


