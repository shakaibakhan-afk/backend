from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

# User Schemas
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=150)
    email: EmailStr

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)

class UserLogin(BaseModel):
    username: str
    password: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=6)

class UserResponse(UserBase):
    id: int
    is_active: bool
    date_joined: datetime
    
    class Config:
        from_attributes = True

# Profile Schemas
class ProfileBase(BaseModel):
    bio: Optional[str] = None
    website: Optional[str] = None
    location: Optional[str] = None
    birth_date: Optional[datetime] = None

class ProfileUpdate(ProfileBase):
    pass

class ProfileResponse(ProfileBase):
    id: int
    user_id: int
    profile_picture: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

# Combined User with Profile
class UserWithProfile(UserResponse):
    profile: Optional[ProfileResponse] = None
    posts_count: Optional[int] = 0
    followers_count: Optional[int] = 0
    following_count: Optional[int] = 0

# Token Schema
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserWithProfile

class RefreshTokenRequest(BaseModel):
    refresh_token: str

