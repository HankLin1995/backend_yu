from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

# Customer schemas
class CustomerBase(BaseModel):
    line_name: str
    line_pic_url: str
    phone: str
    email: Optional[EmailStr]
    address: Optional[str]

class CustomerCreate(CustomerBase):
    line_id: str

class Customer(CustomerBase):
    line_id: str
    create_date: datetime

    class Config:
        from_attributes = True

# Product schemas
class ProductBase(BaseModel):
    product_name: str
    price: float
    description: str
    stock_quantity: int

class ProductCreate(ProductBase):
    special_price: Optional[float] = None

class ProductUpdate(ProductBase):
    special_price: Optional[float] = None

class Product(ProductBase):
    product_id: int
    special_price: Optional[float] = None
    create_time: datetime
    is_deleted: bool

    class Config:
        from_attributes = True

class Photo(BaseModel):
    photo_id: int
    file_path: str
    image_hash: str
    create_time: datetime


class ProductDiscount(BaseModel):
    # discount_id: int
    product_id: int
    quantity: int
    price: float

# Category schemas
class CategoryBase(BaseModel):
    category_name: str

class CategoryCreate(CategoryBase):
    pass

class Category(CategoryBase):
    category_id: int
    
    class Config:
        from_attributes = True

# Order schemas
class OrderDetailBase(BaseModel):
    product_id: int
    quantity: int

class OrderDetailCreate(OrderDetailBase):
    pass

class OrderDetail(BaseModel):
    order_detail_id: int
    order_id: int
    product_id: int
    quantity: int
    unit_price: float
    subtotal: float
    product_deleted: bool = False

    class Config:
        from_attributes = True

class OrderBase(BaseModel):
    line_id: str

class OrderCreate(OrderBase):
    details: List[OrderDetailCreate]

class Order(OrderBase):
    order_id: int
    order_date: datetime
    order_status: str
    total_amount: float
    details: List[OrderDetail]

    class Config:
        from_attributes = True
