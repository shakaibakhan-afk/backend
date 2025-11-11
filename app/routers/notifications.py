from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User, Profile
from app.models.notification import Notification
from app.schemas.notification import NotificationResponse

router = APIRouter()

@router.get("/", response_model=List[NotificationResponse])
def get_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    skip: int = 0,
    limit: int = 50
):
    """Get all notifications for current user"""
    notifications = db.query(Notification).filter(
        Notification.recipient_id == current_user.id
    ).order_by(desc(Notification.timestamp)).offset(skip).limit(limit).all()
    
    return [get_notification_with_details(notification, db) for notification in notifications]

@router.get("/unread", response_model=List[NotificationResponse])
def get_unread_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get unread notifications for current user"""
    notifications = db.query(Notification).filter(
        Notification.recipient_id == current_user.id,
        Notification.is_read == False
    ).order_by(desc(Notification.timestamp)).all()
    
    return [get_notification_with_details(notification, db) for notification in notifications]

@router.get("/unread/count")
def get_unread_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get count of unread notifications"""
    count = db.query(Notification).filter(
        Notification.recipient_id == current_user.id,
        Notification.is_read == False
    ).count()
    
    return {"count": count}

@router.put("/{notification_id}/read", response_model=NotificationResponse)
def mark_notification_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Mark a notification as read"""
    notification = db.query(Notification).filter(Notification.id == notification_id).first()
    
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    if notification.recipient_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    notification.is_read = True
    db.commit()
    db.refresh(notification)
    
    return get_notification_with_details(notification, db)

@router.put("/read-all")
def mark_all_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Mark all notifications as read"""
    db.query(Notification).filter(
        Notification.recipient_id == current_user.id,
        Notification.is_read == False
    ).update({"is_read": True})
    db.commit()
    
    return {"message": "All notifications marked as read"}

@router.delete("/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a notification"""
    notification = db.query(Notification).filter(Notification.id == notification_id).first()
    
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    if notification.recipient_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    db.delete(notification)
    db.commit()
    
    return None

@router.delete("/clear-all", status_code=status.HTTP_204_NO_CONTENT)
def clear_all_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete all notifications for current user"""
    db.query(Notification).filter(
        Notification.recipient_id == current_user.id
    ).delete()
    db.commit()
    
    return None

# Helper function
def get_notification_with_details(notification: Notification, db: Session):
    """Get notification with sender details"""
    sender = None
    sender_profile = None
    
    if notification.sender_id:
        sender = db.query(User).filter(User.id == notification.sender_id).first()
        sender_profile = db.query(Profile).filter(Profile.user_id == notification.sender_id).first()
    
    notification_dict = {
        "id": notification.id,
        "recipient_id": notification.recipient_id,
        "sender_id": notification.sender_id,
        "notification_type": notification.notification_type,
        "message": notification.message,
        "post_id": notification.post_id,
        "is_read": notification.is_read,
        "timestamp": notification.timestamp,
        "sender_username": sender.username if sender else None,
        "sender_profile_picture": sender_profile.profile_picture if sender_profile else None
    }
    
    return NotificationResponse(**notification_dict)

