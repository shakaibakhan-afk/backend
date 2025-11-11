from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class NotificationBase(BaseModel):
    notification_type: str
    message: str
    post_id: Optional[int] = None

class NotificationCreate(NotificationBase):
    recipient_id: int
    sender_id: Optional[int] = None

class NotificationResponse(NotificationBase):
    id: int
    recipient_id: int
    sender_id: Optional[int] = None
    is_read: bool
    timestamp: datetime
    sender_username: Optional[str] = None
    sender_profile_picture: Optional[str] = None
    
    class Config:
        from_attributes = True

