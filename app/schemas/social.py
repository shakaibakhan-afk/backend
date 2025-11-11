from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

# Comment Schemas
class CommentBase(BaseModel):
    text: str = Field(..., min_length=1)

class CommentCreate(CommentBase):
    post_id: int

class CommentResponse(CommentBase):
    id: int
    user_id: int
    post_id: int
    timestamp: datetime
    username: Optional[str] = None
    user_profile_picture: Optional[str] = None
    
    class Config:
        from_attributes = True

# Like Schemas
class LikeCreate(BaseModel):
    post_id: int

class LikeResponse(BaseModel):
    id: int
    user_id: int
    post_id: int
    timestamp: datetime
    
    class Config:
        from_attributes = True

# Follow Schemas
class FollowCreate(BaseModel):
    following_id: int

class FollowResponse(BaseModel):
    id: int
    follower_id: int
    following_id: int
    timestamp: datetime
    
    class Config:
        from_attributes = True

class FollowerInfo(BaseModel):
    id: int
    username: str
    profile_picture: Optional[str] = None
    is_following: bool = False
    
    class Config:
        from_attributes = True

# Story Schemas
class StoryBase(BaseModel):
    caption: Optional[str] = None

class StoryCreate(StoryBase):
    pass

class StoryResponse(StoryBase):
    id: int
    user_id: int
    image: str
    timestamp: datetime
    expires_at: datetime
    username: Optional[str] = None
    user_profile_picture: Optional[str] = None
    
    class Config:
        from_attributes = True

