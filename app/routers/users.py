from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List

from app.core.database import get_db
from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
    verify_refresh_token,
    get_current_active_user
)
from app.models.user import User, Profile
from app.models.post import Post
from app.models.social import Follow
from app.schemas.user import (
    UserCreate,
    UserLogin,
    UserResponse,
    UserWithProfile,
    Token,
    RefreshTokenRequest,
    ProfileUpdate,
    ProfileResponse
)
from app.utils.file_upload import save_upload_file, delete_file
from datetime import timedelta

router = APIRouter()

@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    # Check if user exists
    existing_user = db.query(User).filter(
        (User.username == user_data.username) | (User.email == user_data.email)
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered"
        )
    
    # Create user
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        username=user_data.username,
        email=user_data.email,
        password_hash=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Create profile
    profile = Profile(user_id=db_user.id)
    db.add(profile)
    db.commit()
    db.refresh(profile)
    
    # Create access and refresh tokens
    access_token = create_access_token(data={"sub": str(db_user.id)})
    refresh_token = create_refresh_token(data={"sub": str(db_user.id)})
    
    # Get user with profile
    user_response = get_user_with_stats(db_user, db)
    
    return Token(access_token=access_token, refresh_token=refresh_token, user=user_response)

@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Login user"""
    user = db.query(User).filter(User.username == form_data.username).first()
    
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    # Create access and refresh tokens
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    # Get user with profile
    user_response = get_user_with_stats(user, db)
    
    return Token(access_token=access_token, refresh_token=refresh_token, user=user_response)

@router.post("/refresh", response_model=Token)
def refresh_access_token(refresh_data: RefreshTokenRequest, db: Session = Depends(get_db)):
    """Refresh access token using refresh token"""
    user_id = verify_refresh_token(refresh_data.refresh_token)
    
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user
    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    # Create new access and refresh tokens
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    # Get user with profile
    user_response = get_user_with_stats(user, db)
    
    return Token(access_token=access_token, refresh_token=refresh_token, user=user_response)

@router.get("/me", response_model=UserWithProfile)
def get_current_user_info(current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    """Get current user info"""
    return get_user_with_stats(current_user, db)

@router.get("/", response_model=List[UserWithProfile])
def get_all_users(
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_active_user),
    skip: int = 0,
    limit: int = 50
):
    """Get all users"""
    users = db.query(User).filter(User.is_active == True).offset(skip).limit(limit).all()
    return [get_user_with_stats(user, db, current_user.id) for user in users]

@router.get("/{user_id}", response_model=UserWithProfile)
def get_user(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    """Get user by ID"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return get_user_with_stats(user, db, current_user.id)

@router.get("/username/{username}", response_model=UserWithProfile)
def get_user_by_username(username: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    """Get user by username"""
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return get_user_with_stats(user, db, current_user.id)

@router.put("/profile", response_model=ProfileResponse)
def update_profile(
    profile_data: ProfileUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update user profile"""
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    # Update profile fields
    for field, value in profile_data.dict(exclude_unset=True).items():
        setattr(profile, field, value)
    
    db.commit()
    db.refresh(profile)
    
    return profile

@router.post("/profile/picture")
async def upload_profile_picture(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Upload profile picture"""
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    # Delete old profile picture
    if profile.profile_picture:
        delete_file(profile.profile_picture, "profiles")
    
    # Save new picture
    filename = await save_upload_file(file, "profiles")
    profile.profile_picture = filename
    
    db.commit()
    db.refresh(profile)
    
    return {"message": "Profile picture updated", "filename": filename}

@router.get("/search/{query}", response_model=List[UserWithProfile])
def search_users(
    query: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    limit: int = 20
):
    """Search users by username"""
    users = db.query(User).filter(
        User.username.contains(query)
    ).limit(limit).all()
    
    return [get_user_with_stats(user, db, current_user.id) for user in users]

# Helper function
def get_user_with_stats(user: User, db: Session, current_user_id: int = None):
    """Get user with profile and stats"""
    profile = db.query(Profile).filter(Profile.user_id == user.id).first()
    posts_count = db.query(func.count(Post.id)).filter(Post.user_id == user.id).scalar()
    followers_count = db.query(func.count(Follow.id)).filter(Follow.following_id == user.id).scalar()
    following_count = db.query(func.count(Follow.id)).filter(Follow.follower_id == user.id).scalar()
    
    user_dict = {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "is_active": user.is_active,
        "date_joined": user.date_joined,
        "profile": profile,
        "posts_count": posts_count,
        "followers_count": followers_count,
        "following_count": following_count
    }
    
    return UserWithProfile(**user_dict)

