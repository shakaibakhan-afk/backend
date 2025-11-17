"""
Seed script to populate database with sample data
Run: python scripts/seed_data.py
or: python scripts/run_seed.py (non-interactive)
"""

import os
import sys
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session

backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

from app.core.database import SessionLocal
from app.models.user import User, Profile
from app.models.post import Post, Tag
from app.models.social import Comment, Like, Follow, Story
from app.core.security import get_password_hash

def clear_database(db: Session):
    """Clear all data from database"""
    print("🗑️  Clearing existing data...")
    
    db.query(Comment).delete()
    db.query(Like).delete()
    db.query(Follow).delete()
    db.query(Story).delete()
    db.query(Post).delete()
    db.query(Tag).delete()
    db.query(Profile).delete()
    db.query(User).delete()
    
    db.commit()
    print("✅ Database cleared!")

def create_users(db: Session):
    """Create sample users"""
    print("\n👥 Creating users...")
    
    users_data = [
        {
            "username": "john_doe",
            "email": "john@example.com",
            "password": "password123",
            "bio": "Software Developer | Tech Enthusiast 💻",
            "website": "https://johndoe.com"
        },
        {
            "username": "jane_smith",
            "email": "jane@example.com",
            "password": "password123",
            "bio": "Designer & Artist 🎨 | Creating beautiful things",
            "website": "https://janesmith.design"
        },
        {
            "username": "mike_wilson",
            "email": "mike@example.com",
            "password": "password123",
            "bio": "Photographer 📸 | Travel Lover ✈️",
            "website": "https://mikewilson.photo"
        },
        {
            "username": "sarah_jones",
            "email": "sarah@example.com",
            "password": "password123",
            "bio": "Food Blogger 🍕 | Recipe Creator",
            "website": None
        },
        {
            "username": "alex_brown",
            "email": "alex@example.com",
            "password": "password123",
            "bio": "Fitness Coach 💪 | Healthy Living",
            "website": "https://alexfitness.com"
        }
    ]
    
    users = []
    for user_data in users_data:
        user = User(
            username=user_data["username"],
            email=user_data["email"],
            password_hash=get_password_hash(user_data["password"]),
            is_active=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        profile = Profile(
            user_id=user.id,
            bio=user_data["bio"],
            website=user_data["website"]
        )
        db.add(profile)
        db.commit()
        
        users.append(user)
        print(f"  ✅ Created user: {user.username}")
    
    return users

def create_follows(db: Session, users: list):
    """Create follow relationships"""
    print("\n🔗 Creating follow relationships...")
    
    # john_doe follows everyone
    for user in users[1:]:
        follow = Follow(follower_id=users[0].id, following_id=user.id)
        db.add(follow)
    
    # jane_smith follows john and mike
    follow1 = Follow(follower_id=users[1].id, following_id=users[0].id)
    follow2 = Follow(follower_id=users[1].id, following_id=users[2].id)
    db.add_all([follow1, follow2])
    
    # mike_wilson follows john and jane
    follow3 = Follow(follower_id=users[2].id, following_id=users[0].id)
    follow4 = Follow(follower_id=users[2].id, following_id=users[1].id)
    db.add_all([follow3, follow4])
    
    # sarah_jones follows everyone
    for user in users[:4]:
        follow = Follow(follower_id=users[3].id, following_id=user.id)
        db.add(follow)
    
    # alex_brown follows john and sarah
    follow5 = Follow(follower_id=users[4].id, following_id=users[0].id)
    follow6 = Follow(follower_id=users[4].id, following_id=users[3].id)
    db.add_all([follow5, follow6])
    
    db.commit()
    print("  ✅ Follow relationships created!")

def create_posts(db: Session, users: list):
    """Create sample posts"""
    print("\n📸 Creating posts...")
    
    posts_data = [
        {
            "user": users[0],
            "caption": "Beautiful sunset at the beach 🌅 #nature #sunset",
            "image": "sample_post_1.jpg"
        },
        {
            "user": users[0],
            "caption": "Coffee and code ☕💻 #developer #coding",
            "image": "sample_post_2.jpg"
        },
        {
            "user": users[1],
            "caption": "New design project! What do you think? 🎨",
            "image": "sample_post_3.jpg"
        },
        {
            "user": users[1],
            "caption": "Inspiration from nature 🌿 #design #art",
            "image": "sample_post_4.jpg"
        },
        {
            "user": users[2],
            "caption": "Mountain views from today's hike 🏔️ #photography #travel",
            "image": "sample_post_5.jpg"
        },
        {
            "user": users[2],
            "caption": "Golden hour magic ✨ #photographer #goldenhour",
            "image": "sample_post_6.jpg"
        },
        {
            "user": users[3],
            "caption": "Homemade pizza! Recipe in bio 🍕 #food #cooking",
            "image": "sample_post_7.jpg"
        },
        {
            "user": users[3],
            "caption": "Healthy breakfast bowl 🥗 #healthyfood #breakfast",
            "image": "sample_post_8.jpg"
        },
        {
            "user": users[4],
            "caption": "Leg day complete! 💪 #fitness #gym",
            "image": "sample_post_9.jpg"
        },
        {
            "user": users[4],
            "caption": "Morning workout routine 🏃‍♂️ #fitness #health",
            "image": "sample_post_10.jpg"
        }
    ]
    
    posts = []
    for i, post_data in enumerate(posts_data):
        post = Post(
            user_id=post_data["user"].id,
            caption=post_data["caption"],
            image=post_data["image"],
            is_published=True,
            timestamp=datetime.now(timezone.utc) - timedelta(days=10-i)
        )
        db.add(post)
        db.commit()
        db.refresh(post)
        posts.append(post)
        print(f"  ✅ Created post by {post_data['user'].username}")
    
    return posts

def create_tags(db: Session, posts: list):
    """Create and associate tags with posts"""
    print("\n🏷️  Creating tags...")
    
    tags_data = {
        "nature": [posts[0]],
        "sunset": [posts[0]],
        "developer": [posts[1]],
        "coding": [posts[1]],
        "design": [posts[2], posts[3]],
        "art": [posts[3]],
        "photography": [posts[4]],
        "travel": [posts[4]],
        "photographer": [posts[5]],
        "goldenhour": [posts[5]],
        "food": [posts[6]],
        "cooking": [posts[6]],
        "healthyfood": [posts[7]],
        "breakfast": [posts[7]],
        "fitness": [posts[8], posts[9]],
        "gym": [posts[8]],
        "health": [posts[9]]
    }
    
    for tag_name, tag_posts in tags_data.items():
        tag = Tag(name=tag_name)
        db.add(tag)
        db.commit()
        db.refresh(tag)
        
        for post in tag_posts:
            post.tags.append(tag)
        
        db.commit()
        print(f"  ✅ Created tag: #{tag_name}")

def create_likes(db: Session, users: list, posts: list):
    """Create likes on posts"""
    print("\n❤️  Creating likes...")
    
    # john_doe likes posts from jane and mike
    for post in posts[2:6]:
        like = Like(user_id=users[0].id, post_id=post.id)
        db.add(like)
    
    # jane_smith likes posts from john and mike
    for post in [posts[0], posts[1], posts[4], posts[5]]:
        like = Like(user_id=users[1].id, post_id=post.id)
        db.add(like)
    
    # mike_wilson likes posts from john and jane
    for post in posts[:4]:
        like = Like(user_id=users[2].id, post_id=post.id)
        db.add(like)
    
    # sarah_jones likes food and fitness posts
    for post in [posts[6], posts[7], posts[8], posts[9]]:
        like = Like(user_id=users[3].id, post_id=post.id)
        db.add(like)
    
    # alex_brown likes fitness posts
    for post in posts[8:]:
        like = Like(user_id=users[4].id, post_id=post.id)
        db.add(like)
    
    db.commit()
    print("  ✅ Likes created!")

def create_comments(db: Session, users: list, posts: list):
    """Create comments on posts"""
    print("\n💬 Creating comments...")
    
    comments_data = [
        {"user": users[1], "post": posts[0], "text": "Wow! Amazing view! 😍"},
        {"user": users[2], "post": posts[0], "text": "I need to visit this place!"},
        {"user": users[1], "post": posts[1], "text": "Coffee is life! ☕"},
        {"user": users[0], "post": posts[2], "text": "Love the colors! 🎨"},
        {"user": users[2], "post": posts[2], "text": "This is beautiful!"},
        {"user": users[0], "post": posts[4], "text": "Incredible shot! 📸"},
        {"user": users[1], "post": posts[4], "text": "I want to go there!"},
        {"user": users[3], "post": posts[6], "text": "Looks delicious! 😋"},
        {"user": users[0], "post": posts[6], "text": "Can you share the recipe?"},
        {"user": users[4], "post": posts[8], "text": "Keep it up! 💪"}
    ]
    
    for comment_data in comments_data:
        comment = Comment(
            user_id=comment_data["user"].id,
            post_id=comment_data["post"].id,
            text=comment_data["text"]
        )
        db.add(comment)
    
    db.commit()
    print("  ✅ Comments created!")

def create_stories(db: Session, users: list):
    """Create sample stories"""
    print("\n📖 Creating stories...")
    
    stories_data = [
        {
            "user": users[0],
            "caption": "Working on something exciting! 💻",
            "image": "sample_story_1.jpg",
            "hours_ago": 2
        },
        {
            "user": users[1],
            "caption": "New design inspiration ✨",
            "image": "sample_story_2.jpg",
            "hours_ago": 5
        },
        {
            "user": users[2],
            "caption": "Today's adventure 🏔️",
            "image": "sample_story_3.jpg",
            "hours_ago": 3
        },
        {
            "user": users[3],
            "caption": "Cooking something special 🍳",
            "image": "sample_story_4.jpg",
            "hours_ago": 1
        }
    ]
    
    for story_data in stories_data:
        timestamp = datetime.now(timezone.utc) - timedelta(hours=story_data["hours_ago"])
        expires_at = timestamp + timedelta(hours=24)
        
        story = Story(
            user_id=story_data["user"].id,
            image=story_data["image"],
            media_type="image",
            caption=story_data["caption"],
            timestamp=timestamp,
            expires_at=expires_at
        )
        db.add(story)
        print(f"  ✅ Created story by {story_data['user'].username}")
    
    db.commit()

def print_summary(db: Session):
    """Print summary of seeded data"""
    print("\n" + "="*50)
    print("📊 DATABASE SEEDING SUMMARY")
    print("="*50)
    
    user_count = db.query(User).count()
    post_count = db.query(Post).count()
    comment_count = db.query(Comment).count()
    like_count = db.query(Like).count()
    follow_count = db.query(Follow).count()
    story_count = db.query(Story).count()
    tag_count = db.query(Tag).count()
    
    print(f"👥 Users: {user_count}")
    print(f"📸 Posts: {post_count}")
    print(f"💬 Comments: {comment_count}")
    print(f"❤️  Likes: {like_count}")
    print(f"🔗 Follows: {follow_count}")
    print(f"📖 Stories: {story_count}")
    print(f"🏷️  Tags: {tag_count}")
    print("="*50)
    
    print("\n✅ SEEDING COMPLETE!")
    print("\n📝 Sample Login Credentials:")
    print("   Username: john_doe | Password: password123")
    print("   Username: jane_smith | Password: password123")
    print("   Username: mike_wilson | Password: password123")
    print("   Username: sarah_jones | Password: password123")
    print("   Username: alex_brown | Password: password123")
    print("\n🚀 You can now login and explore the app!")

def main():
    """Main seeding function"""
    print("\n" + "="*50)
    print("🌱 INSTAGRAM CLONE - DATABASE SEEDING")
    print("="*50)
    
    db = SessionLocal()
    
    try:
        response = input("\n⚠️  This will clear all existing data. Continue? (yes/no): ")
        if response.lower() != 'yes':
            print("❌ Seeding cancelled.")
            return
        
        clear_database(db)
        users = create_users(db)
        create_follows(db, users)
        posts = create_posts(db, users)
        create_tags(db, posts)
        create_likes(db, users, posts)
        create_comments(db, users, posts)
        create_stories(db, users)
        
        # Print summary
        print_summary(db)
        
    except Exception as e:
        print(f"\n❌ Error during seeding: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    main()

