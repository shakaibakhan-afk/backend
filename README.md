# Instagram Clone - FastAPI Backend

A full-featured Instagram clone backend built with FastAPI, SQLAlchemy, and JWT authentication.

## Features

- User authentication (register, login, JWT tokens)
- User profiles with customizable bio, profile pictures
- Post creation with image uploads and captions
- Like and unlike posts
- Comment on posts
- Follow/unfollow users

- Real-time notifications
- User search

## Installation

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file (copy from `.env.example`):
```bash
cp .env.example .env
```

4. Edit `.env` and set your SECRET_KEY and other configurations.

## Running the Application

**Option 1: Using the startup script (Recommended)**
```bash
cd backend
# Windows (Batch)
scripts\start_server.bat

# Windows (PowerShell)
scripts\start_server.ps1
```

**Option 2: Manual start**
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- API: http://localhost:8000
- Interactive API docs: http://localhost:8000/docs
- Alternative API docs: http://localhost:8000/redoc

**Note:** All utility scripts are located in the `scripts/` folder. See `scripts/README.md` for details.

## Background Workers (Celery)

Some features (notifications, story cleanup) are processed asynchronously.  
Start Redis (or whichever broker/backend you configured) and run:

**Using scripts (Recommended):**
```bash
# Terminal 1 – Celery worker
# Linux/Mac
./scripts/start_celery_worker.sh

# Windows
scripts\start_celery_worker.bat

# Terminal 2 – Celery beat scheduler
# Linux/Mac
./scripts/start_celery_beat.sh

# Windows
scripts\start_celery_beat.bat
```

**Manual start:**
```bash
# Terminal 1 – Celery worker
celery -A app.celery_app worker --loglevel=info

# Terminal 2 – Celery beat scheduler
celery -A app.celery_app beat --loglevel=info
```

You can monitor tasks with Flower:

```bash
# Using script
# Linux/Mac
./scripts/start_flower.sh

# Windows
scripts\start_flower.bat

# Or manually
celery -A app.celery_app flower --port=5555
```

## Database Migrations (Alembic)

Alembic is preconfigured. Typical workflow:

```bash
alembic revision --autogenerate -m "describe change"
alembic upgrade head
```

See `alembic.ini` and `alembic/env.py` for details. The initial placeholder
revision (`0001_prepare_base.py`) is provided so you can immediately capture the
current schema.

## API Endpoints

### Authentication
- `POST /api/users/register` - Register new user
- `POST /api/users/login` - Login user
- `GET /api/users/me` - Get current user info

### Users & Profiles
- `GET /api/users/{user_id}` - Get user by ID
- `GET /api/users/username/{username}` - Get user by username
- `PUT /api/users/profile` - Update profile
- `POST /api/users/profile/picture` - Upload profile picture
- `GET /api/users/search/{query}` - Search users

### Posts
- `POST /api/posts/` - Create post
- `GET /api/posts/` - Get all posts (feed)
- `GET /api/posts/following` - Get posts from followed users
- `GET /api/posts/{post_id}` - Get specific post
- `GET /api/posts/user/{user_id}` - Get user's posts
- `PUT /api/posts/{post_id}` - Update post
- `DELETE /api/posts/{post_id}` - Delete post

### Social Features
- `POST /api/social/comments` - Create comment
- `GET /api/social/comments/post/{post_id}` - Get post comments
- `DELETE /api/social/comments/{comment_id}` - Delete comment
- `POST /api/social/likes` - Like post
- `DELETE /api/social/likes/post/{post_id}` - Unlike post
- `GET /api/social/likes/post/{post_id}` - Get post likes
- `POST /api/social/follows` - Follow user
- `DELETE /api/social/follows/{user_id}` - Unfollow user
- `GET /api/social/followers/{user_id}` - Get followers
- `GET /api/social/following/{user_id}` - Get following
- `POST /api/social/stories` - Create story
- `GET /api/social/stories` - Get active stories
- `GET /api/social/stories/user/{user_id}` - Get user's stories
- `DELETE /api/social/stories/{story_id}` - Delete story

### Notifications
- `GET /api/notifications/` - Get all notifications
- `GET /api/notifications/unread` - Get unread notifications
- `GET /api/notifications/unread/count` - Get unread count
- `PUT /api/notifications/{notification_id}/read` - Mark as read
- `PUT /api/notifications/read-all` - Mark all as read
- `DELETE /api/notifications/{notification_id}` - Delete notification
- `DELETE /api/notifications/clear-all` - Clear all notifications

## Project Structure

```
backend/
├── app/
│   ├── core/           # Core configuration
│   │   ├── config.py   # Settings
│   │   ├── database.py # Database setup
│   │   └── security.py # JWT & auth
│   ├── models/         # SQLAlchemy models
│   ├── schemas/        # Pydantic schemas
│   ├── routers/        # API endpoints
│   ├── utils/          # Utility functions
│   └── main.py         # FastAPI app
├── uploads/            # User uploaded files
├── requirements.txt
└── README.md
```

