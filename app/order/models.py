from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Numeric, ForeignKey
from sqlalchemy.orm import relationship

from app.db import Base


class Order(Base):
    __tablename__ = "orders"

    order_id = Column(Integer, primary_key=True, index=True)
    line_id = Column(String, ForeignKey("customers.line_id"))
    schedule_id = Column(Integer, ForeignKey("schedules.schedule_id"))
    order_date = Column(DateTime, default=datetime.utcnow)
    order_status = Column(String, default="pending")
    payment_method = Column(String, nullable=True)
    payment_status = Column(String, default="pending")
    total_amount = Column(Numeric(10, 2))
    create_time = Column(DateTime, default=datetime.utcnow)
    update_time = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    customer = relationship("Customer", back_populates="orders")
    schedule = relationship("Schedule", back_populates="orders")
    order_details = relationship("OrderDetail", back_populates="order", cascade="all, delete-orphan")


class OrderDetail(Base):
    __tablename__ = "order_details"

    order_detail_id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.order_id"))
    product_id = Column(Integer, ForeignKey("products.product_id"))
    quantity = Column(Integer)
    unit_price = Column(Numeric(10, 2))
    subtotal = Column(Numeric(10, 2))
    discount_id = Column(Integer, ForeignKey("product_discounts.discount_id"), nullable=True)

    # Relationships
    order = relationship("Order", back_populates="order_details")
    product = relationship("Product", back_populates="order_details")
    discount = relationship("ProductDiscount", back_populates="order_details")
