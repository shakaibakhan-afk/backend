from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from app.core.database import engine, Base
from app.routers import users, posts, social, notifications

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Instagram Clone API",
    description="A full-featured Instagram clone API built with FastAPI",
    version="1.0.0"
)

# CORS configuration - Must be before mounting static files
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173", 
        "http://localhost:5174",  # Alternative Vite port
        "http://localhost:3000", 
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Create uploads directory if it doesn't exist
os.makedirs("uploads/posts", exist_ok=True)
os.makedirs("uploads/profiles", exist_ok=True)
os.makedirs("uploads/stories", exist_ok=True)

# Mount static files
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Include routers
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(posts.router, prefix="/api/posts", tags=["posts"])
app.include_router(social.router, prefix="/api/social", tags=["social"])
app.include_router(notifications.router, prefix="/api/notifications", tags=["notifications"])

@app.get("/")
def read_root():
    return {"message": "Instagram Clone API - Visit /docs for API documentation"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

