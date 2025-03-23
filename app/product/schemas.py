from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from app.photo.schemas import Photo

class CategoryBase(BaseModel):
    category_name: str

class CategoryCreate(CategoryBase):
    pass

class Category(CategoryBase):
    category_id: int
    
    model_config = ConfigDict(from_attributes=True)

class ProductDiscountBase(BaseModel):
    quantity: int = Field(gt=0, description="購買數量")
    price: int = Field(gt=0, description="折扣價格")

class ProductDiscountCreate(ProductDiscountBase):
    pass

class ProductCategory(BaseModel):
    product_id: int
    category_id: int

class ProductCategoryCreate(ProductCategory):
    pass

class ProductDiscount(ProductDiscountBase):
    discount_id: int
    product_id: int

    model_config = ConfigDict(from_attributes=True)

class ProductDiscountsCreate(BaseModel):
    discounts: List[ProductDiscountCreate]

class ProductBase(BaseModel):
    product_name: str = Field(min_length=1, description="商品名稱")
    description: str = Field(description="商品描述")
    price: float = Field(gt=0, description="商品價格")
    one_set_price: Optional[int] = Field(ge=0, description="一組價格")
    one_set_quantity: Optional[int] = Field(ge=0, description="一組數量")
    stock_quantity: int = Field(ge=0, description="庫存數量")
    unit: Optional[str] = Field(description="單位")

class ProductCreate(ProductBase):
    category_ids: Optional[List[int]] = Field(default=None, description="類別ID列表")

class ProductUpdate(ProductBase):
    category_ids: Optional[List[int]] = Field(default=None, description="類別ID列表")

class Product(ProductBase):
    product_id: int
    create_time: datetime
    categories: List[Category] = []
    photos: List[Photo] = []
    discounts: List[ProductDiscount] = []

    model_config = ConfigDict(from_attributes=True)