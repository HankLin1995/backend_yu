from sqlalchemy import Column, String, DateTime, Text
from sqlalchemy.sql import func

from app.db import Base


class Customer(Base):
    __tablename__ = "customers"

    line_id = Column(String, primary_key=True)
    name = Column(String)
    line_name = Column(String, nullable=False)
    line_pic_url = Column(String(1024))
    phone = Column(String(20))
    email = Column(String(255))
    address = Column(Text)
    create_date = Column(DateTime(timezone=True), server_default=func.now())
