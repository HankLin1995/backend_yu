from sqlalchemy import Column, Date, Integer
from sqlalchemy.sql import func

from app.db import Base


class LineBotUsage(Base):
    __tablename__ = "linebot_usage"

    date = Column(Date, primary_key=True, server_default=func.current_date())
    push_count = Column(Integer, default=0, nullable=False)
