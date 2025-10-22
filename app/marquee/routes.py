from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from . import models, schemas
from ..db import get_db

router = APIRouter(prefix="/marquees", tags=["marquees"])

@router.post("/", response_model=schemas.MarqueeResponse)
def create_marquee(marquee: schemas.MarqueeCreate, db: Session = Depends(get_db)):
    """建立新的跑馬燈訊息"""
    db_marquee = models.Marquee(**marquee.dict())
    db.add(db_marquee)
    db.commit()
    db.refresh(db_marquee)
    return db_marquee

@router.get("/", response_model=List[schemas.MarqueeResponse])
def get_all_marquees(db: Session = Depends(get_db)):
    """取得所有跑馬燈訊息"""
    return db.query(models.Marquee).all()

@router.get("/active", response_model=List[schemas.MarqueeResponse])
def get_active_marquees(db: Session = Depends(get_db)):
    """取得所有啟用中的跑馬燈訊息"""
    return db.query(models.Marquee).filter(models.Marquee.is_active == True).all()

@router.get("/{marquee_id}", response_model=schemas.MarqueeResponse)
def get_marquee(marquee_id: int, db: Session = Depends(get_db)):
    """取得特定跑馬燈訊息"""
    marquee = db.query(models.Marquee).filter(models.Marquee.id == marquee_id).first()
    if not marquee:
        raise HTTPException(status_code=404, detail="Marquee not found")
    return marquee

@router.put("/{marquee_id}", response_model=schemas.MarqueeResponse)
def update_marquee(marquee_id: int, marquee: schemas.MarqueeUpdate, db: Session = Depends(get_db)):
    """更新跑馬燈訊息"""
    db_marquee = db.query(models.Marquee).filter(models.Marquee.id == marquee_id).first()
    if not db_marquee:
        raise HTTPException(status_code=404, detail="Marquee not found")
    
    for key, value in marquee.dict(exclude_unset=True).items():
        setattr(db_marquee, key, value)
    
    db.commit()
    db.refresh(db_marquee)
    return db_marquee

@router.delete("/{marquee_id}")
def delete_marquee(marquee_id: int, db: Session = Depends(get_db)):
    """刪除跑馬燈訊息"""
    db_marquee = db.query(models.Marquee).filter(models.Marquee.id == marquee_id).first()
    if not db_marquee:
        raise HTTPException(status_code=404, detail="Marquee not found")
    
    db.delete(db_marquee)
    db.commit()
    return {"message": "Marquee deleted successfully"}
