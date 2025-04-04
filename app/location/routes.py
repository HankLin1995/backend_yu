from datetime import date
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.db import get_db
from . import models, schemas

router = APIRouter()

# 取貨地點相關端點
@router.post("/locations/", response_model=schemas.PickupLocation)
def create_pickup_location(
    location: schemas.PickupLocationCreate,
    db: Session = Depends(get_db)
):
    db_location = models.PickupLocation(**location.model_dump())
    db.add(db_location)
    db.commit()
    db.refresh(db_location)
    return db_location

@router.get("/locations/", response_model=List[schemas.PickupLocation])
def get_pickup_locations(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    locations = db.query(models.PickupLocation).offset(skip).limit(limit).all()
    return locations

@router.get("/locations/{location_id}", response_model=schemas.PickupLocation)
def get_pickup_location(
    location_id: int,
    db: Session = Depends(get_db)
):
    location = db.query(models.PickupLocation).filter(models.PickupLocation.location_id == location_id).first()
    if location is None:
        raise HTTPException(status_code=404, detail="Location not found")
    return location

@router.put("/locations/{location_id}", response_model=schemas.PickupLocation)
def update_pickup_location(
    location_id: int,
    location: schemas.PickupLocationUpdate,
    db: Session = Depends(get_db)
):
    db_location = db.query(models.PickupLocation).filter(models.PickupLocation.location_id == location_id).first()
    if db_location is None:
        raise HTTPException(status_code=404, detail="Location not found")
    
    for key, value in location.model_dump().items():
        setattr(db_location, key, value)
    
    db.commit()
    db.refresh(db_location)
    return db_location

@router.delete("/locations/{location_id}")
def delete_pickup_location(
    location_id: int,
    db: Session = Depends(get_db)
):
    db_location = db.query(models.PickupLocation).filter(models.PickupLocation.location_id == location_id).first()
    if db_location is None:
        raise HTTPException(status_code=404, detail="Location not found")
    
    db.delete(db_location)
    db.commit()
    return {"message": "Location deleted successfully"}

# 日程表相關端點
@router.post("/schedules/", response_model=schemas.Schedule)
def create_schedule(
    schedule: schemas.ScheduleCreate,
    db: Session = Depends(get_db)
):
    # 檢查取貨地點是否存在
    location = db.query(models.PickupLocation).filter(models.PickupLocation.location_id == schedule.location_id).first()
    if location is None:
        raise HTTPException(status_code=404, detail="Location not found")
    
    try:
        db_schedule = models.Schedule(**schedule.model_dump())
        db.add(db_schedule)
        db.commit()
        db.refresh(db_schedule)
        return db_schedule
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Schedule already exists for this date and location")

@router.get("/schedules/", response_model=List[schemas.Schedule])
def get_schedules(
    skip: int = 0,
    limit: int = 100,
    date_filter: date = None,
    db: Session = Depends(get_db)
):
    query = db.query(models.Schedule)
    if date_filter:
        query = query.filter(models.Schedule.date == date_filter)
    schedules = query.offset(skip).limit(limit).all()
    return schedules

@router.get("/schedules/{schedule_id}", response_model=schemas.Schedule)
def get_schedule(
    schedule_id: int,
    db: Session = Depends(get_db)
):
    schedule = db.query(models.Schedule).filter(models.Schedule.schedule_id == schedule_id).first()
    if schedule is None:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return schedule

@router.put("/schedules/{schedule_id}", response_model=schemas.Schedule)
def update_schedule(
    schedule_id: int,
    schedule: schemas.ScheduleUpdate,
    db: Session = Depends(get_db)
):
    db_schedule = db.query(models.Schedule).filter(models.Schedule.schedule_id == schedule_id).first()
    if db_schedule is None:
        raise HTTPException(status_code=404, detail="Schedule not found")
    
    # 檢查取貨地點是否存在
    if schedule.location_id:
        location = db.query(models.PickupLocation).filter(models.PickupLocation.location_id == schedule.location_id).first()
        if location is None:
            raise HTTPException(status_code=404, detail="Location not found")
    
    try:
        for key, value in schedule.model_dump().items():
            setattr(db_schedule, key, value)
        db.commit()
        db.refresh(db_schedule)
        return db_schedule
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Schedule already exists for this date and location")

@router.delete("/schedules/{schedule_id}")
def delete_schedule(
    schedule_id: int,
    db: Session = Depends(get_db)
):
    db_schedule = db.query(models.Schedule).filter(models.Schedule.schedule_id == schedule_id).first()
    if db_schedule is None:
        raise HTTPException(status_code=404, detail="Schedule not found")
    
    db.delete(db_schedule)
    db.commit()
    return {"message": "Schedule deleted successfully"}
