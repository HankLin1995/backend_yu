from datetime import datetime, date, time
from typing import Optional
from pydantic import BaseModel, ConfigDict

class PickupLocationBase(BaseModel):
    district: str
    name: str
    address: Optional[str] = None
    coordinate_x: Optional[float] = None
    coordinate_y: Optional[float] = None
    photo_path: Optional[str] = None

class PickupLocationCreate(PickupLocationBase):
    pass

class PickupLocationUpdate(PickupLocationBase):
    pass

class PickupLocation(PickupLocationBase):
    location_id: int
    create_time: datetime

    model_config = ConfigDict(from_attributes=True)

class ScheduleBase(BaseModel):
    date: date
    location_id: int
    pickup_start_time: time
    pickup_end_time: time
    status: str = "ACTIVE"

class ScheduleCreate(ScheduleBase):
    pass

class ScheduleUpdate(ScheduleBase):
    pass

class Schedule(ScheduleBase):
    schedule_id: int
    create_time: datetime

    model_config = ConfigDict(from_attributes=True)
