from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from datetime import datetime, timedelta

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User, Profile
from app.models.post import Post
from app.models.social import Comment, Like, Follow, Story
from app.schemas.social import (
    CommentCreate,
    CommentResponse,
    LikeCreate,
    LikeResponse,
    FollowCreate,
    FollowResponse,
    FollowerInfo,
    StoryCreate,
    StoryResponse
)
from app.utils.file_upload import save_upload_file, delete_file

router = APIRouter()

# ============ COMMENTS ============
@router.post("/comments", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
def create_comment(
    comment_data: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a comment on a post"""
    # Check if post exists
    post = db.query(Post).filter(Post.id == comment_data.post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # Create comment
    db_comment = Comment(
        user_id=current_user.id,
        post_id=comment_data.post_id,
        text=comment_data.text
    )
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    
    # Create notification for post owner
    if post.user_id != current_user.id:
        from app.models.notification import Notification
        notification = Notification(
            recipient_id=post.user_id,
            sender_id=current_user.id,
            notification_type="comment",
            message=f"{current_user.username} commented on your post",
            post_id=post.id
        )
        db.add(notification)
        db.commit()
    
    return get_comment_with_details(db_comment, db)

@router.get("/comments/post/{post_id}", response_model=List[CommentResponse])
def get_post_comments(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all comments for a post"""
    comments = db.query(Comment).filter(Comment.post_id == post_id).order_by(Comment.timestamp).all()
    return [get_comment_with_details(comment, db) for comment in comments]

@router.delete("/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a comment"""
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    if comment.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this comment")
    
    db.delete(comment)
    db.commit()
    
    return None

# ============ LIKES ============
@router.post("/likes", response_model=LikeResponse, status_code=status.HTTP_201_CREATED)
def like_post(
    like_data: LikeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Like a post"""
    # Check if post exists
    post = db.query(Post).filter(Post.id == like_data.post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # Check if already liked
    existing_like = db.query(Like).filter(
        Like.user_id == current_user.id,
        Like.post_id == like_data.post_id
    ).first()
    
    if existing_like:
        raise HTTPException(status_code=400, detail="Post already liked")
    
    # Create like
    db_like = Like(
        user_id=current_user.id,
        post_id=like_data.post_id
    )
    db.add(db_like)
    db.commit()
    db.refresh(db_like)
    
    # Create notification for post owner
    if post.user_id != current_user.id:
        from app.models.notification import Notification
        notification = Notification(
            recipient_id=post.user_id,
            sender_id=current_user.id,
            notification_type="like",
            message=f"{current_user.username} liked your post",
            post_id=post.id
        )
        db.add(notification)
        db.commit()
    
    return db_like

@router.delete("/likes/post/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def unlike_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Unlike a post"""
    like = db.query(Like).filter(
        Like.user_id == current_user.id,
        Like.post_id == post_id
    ).first()
    
    if not like:
        raise HTTPException(status_code=404, detail="Like not found")
    
    db.delete(like)
    db.commit()
    
    return None

@router.get("/likes/post/{post_id}", response_model=List[FollowerInfo])
def get_post_likes(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get users who liked a post"""
    likes = db.query(Like).filter(Like.post_id == post_id).all()
    
    result = []
    for like in likes:
        user = db.query(User).filter(User.id == like.user_id).first()
        profile = db.query(Profile).filter(Profile.user_id == user.id).first()
        is_following = db.query(Follow).filter(
            Follow.follower_id == current_user.id,
            Follow.following_id == user.id
        ).first() is not None
        
        result.append(FollowerInfo(
            id=user.id,
            username=user.username,
            profile_picture=profile.profile_picture if profile else None,
            is_following=is_following
        ))
    
    return result

# ============ FOLLOWS ============
@router.post("/follows", response_model=FollowResponse, status_code=status.HTTP_201_CREATED)
def follow_user(
    follow_data: FollowCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Follow a user"""
    # Check if user exists
    user = db.query(User).filter(User.id == follow_data.following_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Can't follow yourself
    if follow_data.following_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot follow yourself")
    
    # Check if already following
    existing_follow = db.query(Follow).filter(
        Follow.follower_id == current_user.id,
        Follow.following_id == follow_data.following_id
    ).first()
    
    if existing_follow:
        raise HTTPException(status_code=400, detail="Already following this user")
    
    # Create follow
    db_follow = Follow(
        follower_id=current_user.id,
        following_id=follow_data.following_id
    )
    db.add(db_follow)
    db.commit()
    db.refresh(db_follow)
    
    # Create notification
    from app.models.notification import Notification
    notification = Notification(
        recipient_id=follow_data.following_id,
        sender_id=current_user.id,
        notification_type="follow",
        message=f"{current_user.username} started following you"
    )
    db.add(notification)
    db.commit()
    
    return db_follow

@router.delete("/follows/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def unfollow_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Unfollow a user"""
    follow = db.query(Follow).filter(
        Follow.follower_id == current_user.id,
        Follow.following_id == user_id
    ).first()
    
    if not follow:
        raise HTTPException(status_code=404, detail="Not following this user")
    
    db.delete(follow)
    db.commit()
    
    return None

@router.get("/followers/{user_id}", response_model=List[FollowerInfo])
def get_followers(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get followers of a user"""
    follows = db.query(Follow).filter(Follow.following_id == user_id).all()
    
    result = []
    for follow in follows:
        user = db.query(User).filter(User.id == follow.follower_id).first()
        profile = db.query(Profile).filter(Profile.user_id == user.id).first()
        is_following = db.query(Follow).filter(
            Follow.follower_id == current_user.id,
            Follow.following_id == user.id
        ).first() is not None
        
        result.append(FollowerInfo(
            id=user.id,
            username=user.username,
            profile_picture=profile.profile_picture if profile else None,
            is_following=is_following
        ))
    
    return result

@router.get("/following/{user_id}", response_model=List[FollowerInfo])
def get_following(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get users that a user is following"""
    follows = db.query(Follow).filter(Follow.follower_id == user_id).all()
    
    result = []
    for follow in follows:
        user = db.query(User).filter(User.id == follow.following_id).first()
        profile = db.query(Profile).filter(Profile.user_id == user.id).first()
        is_following = db.query(Follow).filter(
            Follow.follower_id == current_user.id,
            Follow.following_id == user.id
        ).first() is not None
        
        result.append(FollowerInfo(
            id=user.id,
            username=user.username,
            profile_picture=profile.profile_picture if profile else None,
            is_following=is_following
        ))
    
    return result

# ============ STORIES ============
@router.post("/stories", response_model=StoryResponse, status_code=status.HTTP_201_CREATED)
async def create_story(
    caption: Optional[str] = Form(None),
    image: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new story"""
    # Save image
    filename = await save_upload_file(image, "stories")
    
    # Stories expire after 24 hours
    expires_at = datetime.utcnow() + timedelta(hours=24)
    
    # Create story
    db_story = Story(
        user_id=current_user.id,
        image=filename,
        caption=caption,
        expires_at=expires_at
    )
    db.add(db_story)
    db.commit()
    db.refresh(db_story)
    
    return get_story_with_details(db_story, db)

@router.get("/stories", response_model=List[StoryResponse])
def get_stories(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get active stories from followed users"""
    # Get users that current user follows
    following_ids = db.query(Follow.following_id).filter(Follow.follower_id == current_user.id).all()
    following_ids = [fid[0] for fid in following_ids]
    following_ids.append(current_user.id)  # Include current user's stories
    
    # Get active stories
    now = datetime.utcnow()
    stories = db.query(Story).filter(
        Story.user_id.in_(following_ids),
        Story.expires_at > now
    ).order_by(desc(Story.timestamp)).all()
    
    return [get_story_with_details(story, db) for story in stories]

@router.get("/stories/user/{user_id}", response_model=List[StoryResponse])
def get_user_stories(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get active stories from a specific user"""
    now = datetime.utcnow()
    stories = db.query(Story).filter(
        Story.user_id == user_id,
        Story.expires_at > now
    ).order_by(desc(Story.timestamp)).all()
    
    return [get_story_with_details(story, db) for story in stories]

@router.delete("/stories/{story_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_story(
    story_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a story"""
    story = db.query(Story).filter(Story.id == story_id).first()
    
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    
    if story.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this story")
    
    # Delete image file
    delete_file(story.image, "stories")
    
    # Delete story
    db.delete(story)
    db.commit()
    
    return None

# Helper functions
def get_comment_with_details(comment: Comment, db: Session):
    """Get comment with user details"""
    user = db.query(User).filter(User.id == comment.user_id).first()
    profile = db.query(Profile).filter(Profile.user_id == comment.user_id).first()
    
    comment_dict = {
        "id": comment.id,
        "user_id": comment.user_id,
        "post_id": comment.post_id,
        "text": comment.text,
        "timestamp": comment.timestamp,
        "username": user.username if user else None,
        "user_profile_picture": profile.profile_picture if profile else None
    }
    
    return CommentResponse(**comment_dict)

def get_story_with_details(story: Story, db: Session):
    """Get story with user details"""
    user = db.query(User).filter(User.id == story.user_id).first()
    profile = db.query(Profile).filter(Profile.user_id == story.user_id).first()
    
    story_dict = {
        "id": story.id,
        "user_id": story.user_id,
        "image": story.image,
        "caption": story.caption,
        "timestamp": story.timestamp,
        "expires_at": story.expires_at,
        "username": user.username if user else None,
        "user_profile_picture": profile.profile_picture if profile else None
    }
    
    return StoryResponse(**story_dict)

