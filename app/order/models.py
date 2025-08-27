from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Numeric, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from app.db import Base

# STATUS_MAPPING = {
#     "pending": "待處理",
#     "paid": "已付款",
#     "preparing": "準備中",
#     "ready_for_pickup": "可取貨",
#     "partial_completed": "部分完成",
#     "completed": "已完成",
#     "cancelled": "已取消"
# }

class Order(Base):
    __tablename__ = "orders"

    order_id = Column(Integer, primary_key=True, index=True)
    line_id = Column(String(100), ForeignKey("customers.line_id"))
    schedule_id = Column(Integer, ForeignKey("schedules.schedule_id"), nullable=True)  # 允許為 NULL
    order_date = Column(DateTime, default=datetime.utcnow)
    order_status = Column(String(50), default="pending")
    payment_method = Column(String(50), nullable=True)
    payment_status = Column(String(50), default="pending")
    total_amount = Column(Numeric(10, 2))
    delivery_address = Column(String(255), nullable=True)  # 新增配送地址欄位
    delivery_method = Column(String(50), nullable=True)  # 新增配送方式欄位
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
    is_finish = Column(Boolean, default=False)

    # Relationships
    order = relationship("Order", back_populates="order_details")
    product = relationship("Product", back_populates="order_details")
    discount = relationship("ProductDiscount", back_populates="order_details")
