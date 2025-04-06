from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict


class OrderDetailBase(BaseModel):
    product_id: int
    quantity: int
    unit_price: float
    subtotal: float
    discount_id: Optional[int] = None


class OrderDetailCreate(OrderDetailBase):
    pass


class OrderDetail(OrderDetailBase):
    order_detail_id: int
    order_id: int

    model_config = ConfigDict(from_attributes=True)


class OrderBase(BaseModel):
    line_id: str
    schedule_id: int
    payment_method: Optional[str] = None


class OrderCreate(OrderBase):
    order_details: List[OrderDetailCreate]


class Order(OrderBase):
    order_id: int
    order_date: datetime
    order_status: str = Field(default="pending")
    payment_status: str = Field(default="pending")
    total_amount: float
    create_time: datetime
    update_time: datetime
    order_details: List[OrderDetail]

    model_config = ConfigDict(from_attributes=True)


class OrderStatusUpdate(BaseModel):
    order_status: str = Field(
        description="Order status: pending, paid, preparing, ready_for_pickup, completed, cancelled"
    )


class PaymentStatusUpdate(BaseModel):
    payment_status: str = Field(
        description="Payment status: pending, paid, refunded"
    )
