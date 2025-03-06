from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Table, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

# 商品與類別的多對多關聯表
products_categories = Table(
    'products_categories',
    Base.metadata,
    Column('id', Integer, primary_key=True),
    Column('product_id', Integer, ForeignKey('products.product_id')),
    Column('categories_id', Integer, ForeignKey('categories.category_id'))
)

class Customer(Base):
    __tablename__ = "customers"

    line_id = Column(String, primary_key=True)
    line_name = Column(String)
    line_pic_url = Column(String)
    phone = Column(String)
    email = Column(String)
    address = Column(String)
    create_date = Column(DateTime, default=datetime.utcnow)
    
    orders = relationship("Order", back_populates="customer")

class Product(Base):
    __tablename__ = "products"

    product_id = Column(Integer, primary_key=True, index=True)
    product_name = Column(String, index=True)
    price = Column(Float)
    special_price = Column(Float, nullable=True)
    stock_quantity = Column(Integer)
    description = Column(String)
    create_time = Column(DateTime, default=datetime.utcnow)
    
    categories = relationship("Category", secondary=products_categories, back_populates="products")
    photos = relationship("ProductPhoto", back_populates="product")
    orders = relationship("OrderDetail", back_populates="product")

class Category(Base):
    __tablename__ = "categories"

    category_id = Column(Integer, primary_key=True, index=True)
    category_name = Column(String, index=True)
    
    products = relationship("Product", secondary=products_categories, back_populates="categories")

class ProductPhoto(Base):
    __tablename__ = "product_photos"

    photo_id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.product_id"))
    photo_url = Column(String)
    description = Column(String)
    created_date = Column(DateTime, default=datetime.utcnow)
    
    product = relationship("Product", back_populates="photos")

class Order(Base):
    __tablename__ = "orders"

    order_id = Column(Integer, primary_key=True, index=True)
    line_id = Column(String, ForeignKey("customers.line_id"))
    order_date = Column(DateTime, default=datetime.utcnow)
    order_status = Column(String)
    total_amount = Column(Float)
    
    customer = relationship("Customer", back_populates="orders")
    details = relationship("OrderDetail", back_populates="order")

class OrderDetail(Base):
    __tablename__ = "order_details"

    order_detail_id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.order_id"))
    product_id = Column(Integer, ForeignKey("products.product_id"))
    quantity = Column(Integer)
    unit_price = Column(Float)
    subtotal = Column(Float)
    product_deleted = Column(Boolean, default=False)
    
    order = relationship("Order", back_populates="details")
    product = relationship("Product", back_populates="orders")
