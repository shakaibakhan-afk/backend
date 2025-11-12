# 🌱 Database Seeding Guide

This guide explains how to populate your Instagram clone database with sample data for testing.

---

## 📋 What Gets Created

The seed script creates:

- **5 Sample Users** with profiles
- **10 Posts** with images and captions
- **17 Tags** associated with posts
- **Follow Relationships** between users
- **Likes** on various posts
- **Comments** on posts
- **4 Active Stories** (expires in 24 hours)

---

## 🚀 How to Run

### **Step 1: Navigate to Backend**
```bash
cd backend
```

### **Step 2: Activate Virtual Environment**

**Windows:**
```bash
.\venv\Scripts\activate
```

**Mac/Linux:**
```bash
source venv/bin/activate
```

### **Step 3: Run Seed Script**
```bash
python seed_data.py
```

### **Step 4: Confirm**
When prompted, type `yes` to proceed:
```
⚠️  This will clear all existing data. Continue? (yes/no): yes
```

---

## 👥 Sample Users

After seeding, you can login with any of these accounts:

| Username | Email | Password |
|----------|-------|----------|
| `john_doe` | john@example.com | password123 |
| `jane_smith` | jane@example.com | password123 |
| `mike_wilson` | mike@example.com | password123 |
| `sarah_jones` | sarah@example.com | password123 |
| `alex_brown` | alex@example.com | password123 |

---

## 📊 Sample Data Details

### **Users & Profiles**
- **john_doe**: Software Developer | Tech Enthusiast 💻
- **jane_smith**: Designer & Artist 🎨
- **mike_wilson**: Photographer 📸 | Travel Lover ✈️
- **sarah_jones**: Food Blogger 🍕
- **alex_brown**: Fitness Coach 💪

### **Follow Relationships**
- john_doe follows everyone
- jane_smith follows john and mike
- mike_wilson follows john and jane
- sarah_jones follows everyone except alex
- alex_brown follows john and sarah

### **Posts**
Each user has 2 posts with:
- Captions with emojis
- Hashtags
- Sample image filenames
- Timestamps (spread over 10 days)

### **Stories**
4 active stories from different users:
- Created at different times (1-5 hours ago)
- Will auto-expire after 24 hours from creation

---

## ⚠️ Important Notes

### **1. Image Files**
The seed script creates posts and stories with sample filenames like:
- `sample_post_1.jpg`
- `sample_story_1.jpg`

**These files don't actually exist!** You have two options:

#### **Option A: Create Placeholder Images**
Create dummy images in the uploads folder:
```bash
# Create directories
mkdir -p uploads/posts
mkdir -p uploads/stories

# You can add any .jpg files and rename them to match
# Or the app will show broken image icons (which is fine for testing)
```

#### **Option B: Upload Real Content**
After seeding, login and:
1. Create new posts with real images
2. Upload real stories
3. The sample data will still be there for testing relationships

### **2. Clearing Data**
⚠️ **WARNING**: Running the seed script will **DELETE ALL EXISTING DATA**!

Make sure you:
- Backup any important data first
- Are okay with losing current posts, users, etc.

### **3. Database State**
The script will:
- Clear all tables (in correct order to respect foreign keys)
- Create fresh sample data
- Commit all changes

---

## 🔧 Troubleshooting

### **Error: "No module named 'app'"**
Make sure you're running from the `backend` directory:
```bash
cd backend
python seed_data.py
```

### **Error: "Database is locked"**
Stop the backend server first:
```bash
# Stop all Python processes
taskkill /F /IM python.exe  # Windows
pkill python  # Mac/Linux
```

### **Error: Foreign Key Constraint**
The script handles this automatically by deleting in the correct order. If you still see this:
1. Delete the database file: `instagram_clone.db`
2. Restart the backend to recreate tables
3. Run the seed script again

---

## 🧪 Testing Scenarios

After seeding, you can test:

### **1. Login & Authentication**
```
✅ Login with any sample user
✅ JWT tokens work correctly
✅ Session persistence
```

### **2. Feed & Posts**
```
✅ See posts from followed users
✅ Posts show in reverse chronological order
✅ Like/unlike posts
✅ Comment on posts
```

### **3. Stories**
```
✅ View active stories
✅ Stories auto-expire after 24 hours
✅ Create new stories
✅ Delete own stories
```

### **4. Social Features**
```
✅ Follow/unfollow users
✅ View followers/following lists
✅ See follower counts
```

### **5. Profile**
```
✅ View user profiles
✅ Edit own profile
✅ See user's posts
✅ See user's stats
```

---

## 🔄 Re-seeding

To re-seed the database:

1. **Stop the backend** (if running)
2. **Run seed script** again:
   ```bash
   python seed_data.py
   ```
3. **Type `yes`** when prompted
4. **Restart backend**

All data will be reset to the sample data.

---

## 📝 Customizing Seed Data

To customize the sample data, edit `seed_data.py`:

### **Add More Users**
```python
users_data = [
    {
        "username": "new_user",
        "email": "new@example.com",
        "password": "password123",
        "bio": "Your bio here",
        "website": "https://example.com"
    },
    # ... existing users
]
```

### **Add More Posts**
```python
posts_data = [
    {
        "user": users[0],
        "caption": "Your caption #hashtag",
        "image": "your_image.jpg"
    },
    # ... existing posts
]
```

### **Change Relationships**
Modify the `create_follows()` function to change who follows whom.

---

## ✅ Success!

After seeding, you should see:

```
📊 DATABASE SEEDING SUMMARY
==================================================
👥 Users: 5
📸 Posts: 10
💬 Comments: 10
❤️  Likes: 20
🔗 Follows: 12
📖 Stories: 4
🏷️  Tags: 17
==================================================

✅ SEEDING COMPLETE!

📝 Sample Login Credentials:
   Username: john_doe | Password: password123
   ...
```

Now you can login and test all features! 🚀

---

## 🎯 Next Steps

1. **Login** with a sample user
2. **Explore** the feed and stories
3. **Create** new posts and stories
4. **Interact** with existing content
5. **Test** all features

Happy testing! 🎉

