from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Optional

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User, Profile
from app.models.post import Post, Tag, post_tags
from app.models.social import Like, Comment
from app.schemas.post import PostCreate, PostUpdate, PostResponse, TagResponse
from app.utils.file_upload import save_upload_file, delete_file

router = APIRouter()

@router.post("/", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(
    caption: Optional[str] = Form(None),
    image: UploadFile = File(...),
    tags: Optional[str] = Form(None),  # Comma-separated tags
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new post"""
    # Save image
    filename = await save_upload_file(image, "posts")
    
    # Create post
    db_post = Post(
        user_id=current_user.id,
        caption=caption,
        image=filename,
        is_published=True
    )
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    
    # Handle tags
    if tags:
        tag_names = [tag.strip().lower() for tag in tags.split(",") if tag.strip()]
        for tag_name in tag_names:
            # Get or create tag
            db_tag = db.query(Tag).filter(Tag.name == tag_name).first()
            if not db_tag:
                db_tag = Tag(name=tag_name)
                db.add(db_tag)
                db.commit()
                db.refresh(db_tag)
            # Associate tag with post
            db_post.tags.append(db_tag)
        db.commit()
    
    return get_post_with_details(db_post, db, current_user.id)

@router.get("/", response_model=List[PostResponse])
def get_posts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    skip: int = 0,
    limit: int = 20
):
    """Get posts from followed users only (personalized feed)"""
    from app.models.social import Follow
    
    # Get users that current user follows
    following_ids = db.query(Follow.following_id).filter(Follow.follower_id == current_user.id).all()
    following_ids = [fid[0] for fid in following_ids]
    following_ids.append(current_user.id)  # Include current user's posts
    
    # Only show posts from followed users
    posts = db.query(Post).filter(
        Post.user_id.in_(following_ids),
        Post.is_published == True
    ).order_by(desc(Post.timestamp)).offset(skip).limit(limit).all()
    
    return [get_post_with_details(post, db, current_user.id) for post in posts]

@router.get("/following", response_model=List[PostResponse])
def get_following_posts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    skip: int = 0,
    limit: int = 20
):
    """Get posts from users that current user follows"""
    from app.models.social import Follow
    
    # Get users that current user follows
    following_ids = db.query(Follow.following_id).filter(Follow.follower_id == current_user.id).all()
    following_ids = [fid[0] for fid in following_ids]
    following_ids.append(current_user.id)  # Include current user's posts
    
    posts = db.query(Post).filter(
        Post.user_id.in_(following_ids),
        Post.is_published == True
    ).order_by(desc(Post.timestamp)).offset(skip).limit(limit).all()
    
    return [get_post_with_details(post, db, current_user.id) for post in posts]

@router.get("/{post_id}", response_model=PostResponse)
def get_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific post (only if from followed user or own post)"""
    from app.models.social import Follow
    
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # Check if user is authorized to view this post
    # User can view if: 1) It's their own post, or 2) They follow the post owner
    if post.user_id != current_user.id:
        is_following = db.query(Follow).filter(
            Follow.follower_id == current_user.id,
            Follow.following_id == post.user_id
        ).first()
        
        if not is_following:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only view posts from users you follow"
            )
    
    return get_post_with_details(post, db, current_user.id)

@router.get("/user/{user_id}", response_model=List[PostResponse])
def get_user_posts(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    skip: int = 0,
    limit: int = 20
):
    """Get posts by a specific user (only if followed or own profile)"""
    from app.models.social import Follow
    
    # Check if user is authorized to view this user's posts
    # User can view if: 1) It's their own profile, or 2) They follow this user
    if user_id != current_user.id:
        is_following = db.query(Follow).filter(
            Follow.follower_id == current_user.id,
            Follow.following_id == user_id
        ).first()
        
        if not is_following:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only view posts from users you follow"
            )
    
    posts = db.query(Post).filter(
        Post.user_id == user_id,
        Post.is_published == True
    ).order_by(desc(Post.timestamp)).offset(skip).limit(limit).all()
    
    return [get_post_with_details(post, db, current_user.id) for post in posts]

@router.put("/{post_id}", response_model=PostResponse)
def update_post(
    post_id: int,
    post_data: PostUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update a post"""
    post = db.query(Post).filter(Post.id == post_id).first()
    
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    if post.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this post")
    
    # Update caption
    if post_data.caption is not None:
        post.caption = post_data.caption
    
    # Update tags
    if post_data.tags is not None:
        # Clear existing tags
        post.tags = []
        # Add new tags
        for tag_name in post_data.tags:
            tag_name = tag_name.strip().lower()
            if tag_name:
                db_tag = db.query(Tag).filter(Tag.name == tag_name).first()
                if not db_tag:
                    db_tag = Tag(name=tag_name)
                    db.add(db_tag)
                    db.commit()
                    db.refresh(db_tag)
                post.tags.append(db_tag)
    
    db.commit()
    db.refresh(post)
    
    return get_post_with_details(post, db, current_user.id)

@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a post"""
    post = db.query(Post).filter(Post.id == post_id).first()
    
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    if post.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this post")
    
    # Delete image file
    delete_file(post.image, "posts")
    
    # Delete post (cascade will handle comments and likes)
    db.delete(post)
    db.commit()
    
    return None

# Helper function
def get_post_with_details(post: Post, db: Session, current_user_id: int = None):
    """Get post with user details, likes count, comments count, and is_liked status"""
    user = db.query(User).filter(User.id == post.user_id).first()
    profile = db.query(Profile).filter(Profile.user_id == post.user_id).first()
    
    likes_count = db.query(func.count(Like.id)).filter(Like.post_id == post.id).scalar()
    comments_count = db.query(func.count(Comment.id)).filter(Comment.post_id == post.id).scalar()
    
    is_liked = False
    if current_user_id:
        is_liked = db.query(Like).filter(
            Like.post_id == post.id,
            Like.user_id == current_user_id
        ).first() is not None
    
    post_dict = {
        "id": post.id,
        "user_id": post.user_id,
        "caption": post.caption,
        "image": post.image,
        "is_published": post.is_published,
        "scheduled_time": post.scheduled_time,
        "timestamp": post.timestamp,
        "username": user.username if user else None,
        "user_profile_picture": profile.profile_picture if profile else None,
        "likes_count": likes_count,
        "comments_count": comments_count,
        "tags": post.tags,
        "is_liked": is_liked
    }
    
    return PostResponse(**post_dict)

