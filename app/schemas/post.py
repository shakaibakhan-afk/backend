from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

# Tag Schemas
class TagBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)

class TagCreate(TagBase):
    pass

class TagResponse(TagBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Post Schemas
class PostBase(BaseModel):
    caption: Optional[str] = None
    scheduled_time: Optional[datetime] = None

class PostCreate(PostBase):
    tags: Optional[List[str]] = []

class PostUpdate(BaseModel):
    caption: Optional[str] = None
    tags: Optional[List[str]] = None

class PostResponse(PostBase):
    id: int
    user_id: int
    image: str
    is_published: bool
    timestamp: datetime
    username: Optional[str] = None
    user_profile_picture: Optional[str] = None
    likes_count: Optional[int] = 0
    comments_count: Optional[int] = 0
    tags: List[TagResponse] = []
    is_liked: Optional[bool] = False
    
    class Config:
        from_attributes = True

