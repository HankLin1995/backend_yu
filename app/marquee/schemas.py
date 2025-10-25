from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class MarqueeBase(BaseModel):
    message: str
    is_active: bool = True

class MarqueeCreate(MarqueeBase):
    pass

class MarqueeUpdate(BaseModel):
    message: Optional[str] = None
    is_active: Optional[bool] = None

class MarqueeResponse(MarqueeBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
