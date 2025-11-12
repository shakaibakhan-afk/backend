import os
import uuid
from pathlib import Path
from fastapi import UploadFile, HTTPException
from app.core.config import settings

async def save_upload_file(upload_file: UploadFile, folder: str) -> str:
    """Save an uploaded file and return its filename"""
    
    # Check file extension
    file_ext = Path(upload_file.filename).suffix.lower()
    if file_ext not in settings.ALLOWED_IMAGE_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed types: {', '.join(settings.ALLOWED_IMAGE_EXTENSIONS)}"
        )
    
    # Generate unique filename
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    file_path = os.path.join("uploads", folder, unique_filename)
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    # Read and validate file size
    contents = await upload_file.read()
    if len(contents) > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {settings.MAX_FILE_SIZE / (1024*1024)}MB"
        )
    
    # Save file
    with open(file_path, "wb") as f:
        f.write(contents)
    
    return unique_filename

async def save_media_file(upload_file: UploadFile, folder: str) -> tuple:
    """Save an uploaded media file (image or video) and return (filename, media_type)"""
    
    # Check file extension
    file_ext = Path(upload_file.filename).suffix.lower()
    
    # Define allowed extensions
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
    video_extensions = ['.mp4', '.mov', '.avi', '.webm', '.mkv']
    allowed_extensions = image_extensions + video_extensions
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed types: images ({', '.join(image_extensions)}) or videos ({', '.join(video_extensions)})"
        )
    
    # Determine media type
    media_type = "image" if file_ext in image_extensions else "video"
    
    # Generate unique filename
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    file_path = os.path.join("uploads", folder, unique_filename)
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    # Read and validate file size (allow larger files for videos)
    contents = await upload_file.read()
    max_size = settings.MAX_FILE_SIZE * 5 if media_type == "video" else settings.MAX_FILE_SIZE  # 5x larger for videos
    
    if len(contents) > max_size:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size for {media_type}: {max_size / (1024*1024):.1f}MB"
        )
    
    # Save file
    with open(file_path, "wb") as f:
        f.write(contents)
    
    return unique_filename, media_type

def delete_file(filename: str, folder: str):
    """Delete a file from the uploads folder"""
    if filename:
        file_path = os.path.join("uploads", folder, filename)
        if os.path.exists(file_path):
            os.remove(file_path)

