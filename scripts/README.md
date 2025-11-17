# Backend Scripts

This folder contains utility scripts for the Instagram Clone backend.

## Available Scripts

### Server Startup

- **`start_server.bat`** / **`start_server.ps1`** - Start the FastAPI backend server
  ```bash
  # Windows (Batch)
  scripts\start_server.bat
  
  # Windows (PowerShell)
  scripts\start_server.ps1
  ```

### Database & Migrations

- **`seed_data.py`** - Interactive database seeding script (asks for confirmation)
  ```bash
  python scripts/seed_data.py
  ```

- **`run_seed.py`** - Non-interactive database seeding script (auto-confirms)
  ```bash
  python scripts/run_seed.py
  ```

**Note:** Database migrations are handled by Alembic. See the main README.md for migration instructions.

### Celery Workers

- **`start_celery_worker.sh`** / **`start_celery_worker.bat`** - Start Celery worker
  ```bash
  # Linux/Mac
  ./scripts/start_celery_worker.sh
  
  # Windows
  scripts\start_celery_worker.bat
  ```

- **`start_celery_beat.sh`** / **`start_celery_beat.bat`** - Start Celery beat scheduler
  ```bash
  # Linux/Mac
  ./scripts/start_celery_beat.sh
  
  # Windows
  scripts\start_celery_beat.bat
  ```

- **`start_flower.sh`** / **`start_flower.bat`** - Start Flower monitoring (http://localhost:5555)
  ```bash
  # Linux/Mac
  ./scripts/start_flower.sh
  
  # Windows
  scripts\start_flower.bat
  ```

### Code Quality

- **`lint.py`** - Run Black linter (check mode)
  ```bash
  python scripts/lint.py
  ```

## Notes

- All scripts assume they are run from the `backend` directory
- Make sure your virtual environment is activated before running scripts
- Celery scripts require Redis to be running on localhost:6379

