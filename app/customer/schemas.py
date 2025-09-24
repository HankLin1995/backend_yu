from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class CustomerBase(BaseModel):
    line_name: str
    name: Optional[str] = None
    line_pic_url: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    ban: Optional[bool] = False


class CustomerCreate(CustomerBase):
    line_id: str


class CustomerUpdate(CustomerBase):
    pass


class CustomerBanUpdate(BaseModel):
    ban: bool


class Customer(CustomerBase):
    line_id: str
    create_date: datetime

    model_config = ConfigDict(from_attributes=True)
