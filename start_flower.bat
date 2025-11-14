@echo off
echo Starting Flower (Celery Monitoring)...
echo.
echo Make sure Redis is running on localhost:6379
echo Open http://localhost:5555 in your browser
echo.

cd /d "%~dp0"
call venv\Scripts\activate.bat
celery -A app.celery_app flower --port=5555

pause



