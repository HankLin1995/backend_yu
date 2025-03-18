from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.db import get_db
from . import models
from ..product import schemas
import os
from datetime import datetime
import hashlib

router = APIRouter(prefix="/photos", tags=["photos"])

def get_upload_dir():
    """Get the upload directory path from environment or default"""
    upload_dir = os.getenv('UPLOAD_DIR', os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads"))
    os.makedirs(upload_dir, exist_ok=True)
    return upload_dir

@router.post("/upload/", response_model=schemas.Photo)
async def upload_photo(
    file: UploadFile = File(...),
    product_id: int = Form(...),
    db: Session = Depends(get_db)
):
    """
    Upload photo endpoint
    
    Args:
        file: The uploaded file, must be an image
        product_id: Product ID to associate with the photo
        
    Returns:
        ProductPhoto: Created photo record
    """
    # Validate file type
    allowed_types = [".jpg", ".jpeg", ".png", ".gif"]
    file_extension = os.path.splitext(file.filename)[1].lower()
    
    if file_extension not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail="Only JPG, JPEG, PNG or GIF images are allowed"
        )
    
    try:
        # Generate unique filename with timestamp
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        new_filename = f"{timestamp}{file_extension}"
        file_path = os.path.join(get_upload_dir(), new_filename)
        
        # Save file
        contents = await file.read()
        with open(file_path, "wb") as f:
            f.write(contents)
        
        # Calculate image hash for duplicate detection
        file_hash = hashlib.md5(contents).hexdigest()
            
        # Check for duplicate image
        existing_photo = db.query(models.ProductPhoto).filter(
            models.ProductPhoto.image_hash == file_hash
        ).first()
        if existing_photo:
            # If file exists, delete the uploaded file
            os.remove(file_path)
            raise HTTPException(status_code=400, detail="This photo already exists")
        
        # Create database record
        db_photo = models.ProductPhoto(
            product_id=product_id,
            file_path=new_filename,
            image_hash=file_hash
        )
        
        db.add(db_photo)
        db.commit()
        db.refresh(db_photo)
        return db_photo
        
    except HTTPException:
        raise
    except Exception as e:
        # Clean up uploaded file if error occurs
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)
        db.rollback()
        raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")

@router.get("/{photo_id}", response_model=schemas.Photo)
def get_photo(photo_id: int, db: Session = Depends(get_db)):
    """Get photo by ID"""
    photo = db.query(models.ProductPhoto).filter(models.ProductPhoto.photo_id == photo_id).first()
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")
    return photo

@router.delete("/{photo_id}")
def delete_photo(photo_id: int, db: Session = Depends(get_db)):
    """Delete photo by ID"""
    photo = db.query(models.ProductPhoto).filter(models.ProductPhoto.photo_id == photo_id).first()
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")
    
    # Delete physical file
    file_path = os.path.join(get_upload_dir(), photo.file_path)
    if os.path.exists(file_path):
        os.remove(file_path)
    
    # Delete database record
    db.delete(photo)
    db.commit()
    
    return {"message": "Photo deleted successfully"}
