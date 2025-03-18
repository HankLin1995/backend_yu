from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from datetime import datetime
from app.db import Base
from sqlalchemy.orm import relationship

class ProductPhoto(Base):
    __tablename__ = "product_photos"

    photo_id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.product_id"))
    file_path = Column(String)
    image_hash = Column(String, index=True)
    create_time = Column(DateTime, default=datetime.utcnow)
    
    product = relationship("Product", back_populates="photos")
