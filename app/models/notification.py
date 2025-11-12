from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class Notification(Base):
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    recipient_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    sender_id = Column(Integer, nullable=True)  # Can be null for system notifications
    notification_type = Column(String(50), nullable=False)  # like, comment, follow, reply, etc.
    message = Column(Text, nullable=False)
    post_id = Column(Integer, nullable=True)  # Related post if applicable
    comment_id = Column(Integer, nullable=True)  # Related comment if applicable
    is_read = Column(Boolean, default=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    recipient = relationship("User", back_populates="notifications")

