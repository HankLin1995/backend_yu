from typing import List
from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db import get_db
from . import models, schemas

router = APIRouter(prefix="/linebot-usage", tags=["linebot-usage"])


@router.post("/", response_model=schemas.LineBotUsage)
def create_usage_record(usage: schemas.LineBotUsageCreate, db: Session = Depends(get_db)):
    """創建新的用量記錄"""
    db_usage = db.query(models.LineBotUsage).filter(models.LineBotUsage.date == usage.date).first()
    if db_usage:
        raise HTTPException(status_code=400, detail="Usage record for this date already exists")
    
    db_usage = models.LineBotUsage(**usage.model_dump())
    db.add(db_usage)
    db.commit()
    db.refresh(db_usage)
    return db_usage


@router.get("/{usage_date}", response_model=schemas.LineBotUsage)
def get_usage_by_date(usage_date: date, db: Session = Depends(get_db)):
    """查詢特定日期的用量"""
    db_usage = db.query(models.LineBotUsage).filter(models.LineBotUsage.date == usage_date).first()
    if not db_usage:
        raise HTTPException(status_code=404, detail="Usage record not found")
    return db_usage


@router.get("/", response_model=List[schemas.LineBotUsage])
def list_usage(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """列出所有用量記錄（按日期降序）"""
    usages = db.query(models.LineBotUsage).order_by(models.LineBotUsage.date.desc()).offset(skip).limit(limit).all()
    return usages


@router.post("/increment", response_model=schemas.LineBotUsage)
def increment_today_usage(db: Session = Depends(get_db)):
    """增加今日的推送次數（自動創建或更新）"""
    today = date.today()
    db_usage = db.query(models.LineBotUsage).filter(models.LineBotUsage.date == today).first()
    
    if not db_usage:
        # 如果今日記錄不存在，創建新記錄
        db_usage = models.LineBotUsage(date=today, push_count=1)
        db.add(db_usage)
    else:
        # 如果存在，增加計數
        db_usage.push_count += 1
    
    db.commit()
    db.refresh(db_usage)
    return db_usage


@router.put("/{usage_date}", response_model=schemas.LineBotUsage)
def update_usage(usage_date: date, usage: schemas.LineBotUsageUpdate, db: Session = Depends(get_db)):
    """更新特定日期的用量"""
    db_usage = db.query(models.LineBotUsage).filter(models.LineBotUsage.date == usage_date).first()
    if not db_usage:
        raise HTTPException(status_code=404, detail="Usage record not found")
    
    db_usage.push_count = usage.push_count
    db.commit()
    db.refresh(db_usage)
    return db_usage


@router.get("/stats/monthly", response_model=dict)
def get_monthly_stats(year: int, month: int, db: Session = Depends(get_db)):
    """查詢特定月份的統計資料"""
    # 計算該月的第一天和最後一天
    first_day = date(year, month, 1)
    if month == 12:
        last_day = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        last_day = date(year, month + 1, 1) - timedelta(days=1)
    
    # 查詢該月的所有記錄
    usages = db.query(models.LineBotUsage).filter(
        models.LineBotUsage.date >= first_day,
        models.LineBotUsage.date <= last_day
    ).all()
    
    # 計算統計數據
    total_pushes = sum(usage.push_count for usage in usages)
    avg_pushes = total_pushes / len(usages) if usages else 0
    max_pushes = max((usage.push_count for usage in usages), default=0)
    
    return {
        "year": year,
        "month": month,
        "total_pushes": total_pushes,
        "average_pushes": round(avg_pushes, 2),
        "max_pushes": max_pushes,
        "days_recorded": len(usages)
    }


@router.delete("/{usage_date}")
def delete_usage(usage_date: date, db: Session = Depends(get_db)):
    """刪除特定日期的用量記錄"""
    db_usage = db.query(models.LineBotUsage).filter(models.LineBotUsage.date == usage_date).first()
    if not db_usage:
        raise HTTPException(status_code=404, detail="Usage record not found")
    
    db.delete(db_usage)
    db.commit()
    return {"message": "Usage record deleted successfully"}
