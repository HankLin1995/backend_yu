from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from datetime import datetime
from app.db import Base

class Photo(Base):
    __tablename__ = "photos"

    PhotoID = Column(Integer, primary_key=True, autoincrement=True)
    ProductID = Column(Integer, ForeignKey("products.product_id"), nullable=True)
    FilePath = Column(String, nullable=True)  # 儲存檔案路徑
    ImageHash = Column(String, nullable=False)
    CreateTime = Column(DateTime, default=datetime.utcnow)
