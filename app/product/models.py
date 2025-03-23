from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Table, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from ..db import Base

# # # 商品與類別的多對多關聯表
# products_categories = Table(
#     'products_categories',
#     Base.metadata,
#     Column('id', Integer, primary_key=True),
#     Column('product_id', Integer, ForeignKey('products.product_id')),
#     Column('categories_id', Integer, ForeignKey('categories.category_id'))
# )

class ProductsCategories(Base):
    __tablename__ = "products_categories"

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.product_id")) # 商品ID
    category_id = Column(Integer, ForeignKey("categories.category_id")) # 類別ID

class Product(Base):
    __tablename__ = "products"

    product_id = Column(Integer, primary_key=True, index=True)
    product_name = Column(String, index=True)
    description = Column(String)
    price = Column(Float)  # 價格
    one_set_price = Column(Integer, nullable=True)  # 一組價格
    one_set_quantity = Column(Integer, nullable=True)  # 一組數量
    stock_quantity = Column(Integer)  # 庫存
    unit = Column(String, nullable=True)  # 單位
    create_time = Column(DateTime, default=datetime.utcnow)
    # is_deleted = Column(Boolean, default=False)
    
    categories = relationship("Category", secondary="products_categories", back_populates="products")
    photos = relationship("ProductPhoto", back_populates="product")
    # orders = relationship("OrderDetail", back_populates="product")
    discounts = relationship("ProductDiscount", back_populates="product")

class Category(Base):
    __tablename__ = "categories"

    category_id = Column(Integer, primary_key=True, index=True)
    category_name = Column(String, index=True)
    
    products = relationship("Product", secondary="products_categories", back_populates="categories")

class ProductDiscount(Base):
    __tablename__ = "product_discounts"

    discount_id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.product_id"))
    quantity = Column(Integer)
    price = Column(Integer)  # Changed from Float to Integer
    
    product = relationship("Product", back_populates="discounts")