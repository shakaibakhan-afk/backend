#Requires -Version 5.1
# Instagram Clone Backend Server Startup Script
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Instagram Clone Backend Server" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Change to backend directory (parent of scripts folder)
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$backendDir = Split-Path -Parent $scriptDir
Set-Location $backendDir

# Check if venv exists
$venvPython = Join-Path $backendDir "venv\Scripts\python.exe"
if (-not (Test-Path $venvPython)) {
    Write-Host "ERROR: Virtual environment not found!" -ForegroundColor Red
    Write-Host "Please create it first: python -m venv venv" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if .env exists, create if not
if (-not (Test-Path ".env")) {
    Write-Host "Creating .env file with secure keys..." -ForegroundColor Yellow
    & $venvPython -c @"
import secrets
secret_key = secrets.token_hex(32)
refresh_key = secrets.token_hex(32)
with open('.env', 'w') as f:
    f.write(f'''DATABASE_URL=sqlite:///./instagram_clone.db
SECRET_KEY={secret_key}
REFRESH_SECRET_KEY={refresh_key}
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=30
DEBUG=True
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
MAX_FILE_SIZE=5242880
STORY_EXPIRY_HOURS=24
APP_NAME=Instagram Clone
''')
"@
    Write-Host ".env file created!" -ForegroundColor Green
    Write-Host ""
}

# Verify we're using venv Python
Write-Host "Using Python:" -ForegroundColor Cyan
& $venvPython --version
Write-Host ""

# Verify we're in the right directory
Write-Host "Current directory: $PWD" -ForegroundColor Cyan
Write-Host ""

# Start the server using venv Python
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Starting uvicorn server..." -ForegroundColor Green
Write-Host "Server will be available at: http://127.0.0.1:8000" -ForegroundColor Yellow
Write-Host "API docs at: http://127.0.0.1:8000/docs" -ForegroundColor Yellow
Write-Host "Press CTRL+C to stop the server" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Use venv Python explicitly
& $venvPython -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

