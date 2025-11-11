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

def delete_file(filename: str, folder: str):
    """Delete a file from the uploads folder"""
    if filename and filename != "default-avatar.jpg":
        file_path = os.path.join("uploads", folder, filename)
        if os.path.exists(file_path):
            os.remove(file_path)

