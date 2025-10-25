from sqlalchemy import Column, Integer, String, Boolean, DateTime
from datetime import datetime
from ..db import Base

class Marquee(Base):
    __tablename__ = "marquees"

    id = Column(Integer, primary_key=True, index=True)
    message = Column(String(500), nullable=False)  # 跑馬燈訊息內容
    is_active = Column(Boolean, default=True)  # 是否啟用
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
