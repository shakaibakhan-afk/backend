@echo off
echo ========================================
echo Instagram Clone Backend Server
echo ========================================
echo.

REM Change to backend directory (parent of scripts folder)
cd /d "%~dp0.."

REM Check if venv exists
if not exist "venv\Scripts\python.exe" (
    echo ERROR: Virtual environment not found!
    echo Please create it first: python -m venv venv
    pause
    exit /b 1
)

REM Use venv Python explicitly (NOT system Python)
set VENV_PYTHON=%~dp0venv\Scripts\python.exe

REM Check if .env exists, create if not
if not exist .env (
    echo Creating .env file with secure keys...
    %VENV_PYTHON% -c "import secrets; secret_key = secrets.token_hex(32); refresh_key = secrets.token_hex(32); open('.env', 'w').write(f'DATABASE_URL=sqlite:///./instagram_clone.db\nSECRET_KEY={secret_key}\nREFRESH_SECRET_KEY={refresh_key}\nALGORITHM=HS256\nACCESS_TOKEN_EXPIRE_MINUTES=30\nREFRESH_TOKEN_EXPIRE_DAYS=30\nDEBUG=True\nCELERY_BROKER_URL=redis://localhost:6379/0\nCELERY_RESULT_BACKEND=redis://localhost:6379/0\nMAX_FILE_SIZE=5242880\nSTORY_EXPIRY_HOURS=24\nAPP_NAME=Instagram Clone\n')"
    echo .env file created!
    echo.
)

REM Verify we're using venv Python
echo Using Python: 
%VENV_PYTHON% --version
echo.

REM Verify we're in the right directory
echo Current directory: %CD%
echo.

REM Start the server using venv Python
echo ========================================
echo Starting uvicorn server...
echo Server will be available at: http://127.0.0.1:8000
echo API docs at: http://127.0.0.1:8000/docs
echo Press CTRL+C to stop the server
echo ========================================
echo.

%VENV_PYTHON% -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

pause

