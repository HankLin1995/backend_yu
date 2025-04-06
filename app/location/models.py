from datetime import datetime, date, time
from sqlalchemy import Column, Integer, String, Text, DECIMAL, DateTime, Date, Time, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.db import Base

class PickupLocation(Base):
    __tablename__ = "pickup_locations"

    location_id = Column(Integer, primary_key=True, index=True)
    district = Column(String(50), nullable=False)
    name = Column(String(100), nullable=False)
    address = Column(Text, nullable=True)
    coordinate_x = Column(DECIMAL(10, 6), nullable=True)
    coordinate_y = Column(DECIMAL(10, 6), nullable=True)
    photo_path = Column(String(255), nullable=True)
    create_time = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    schedules = relationship("Schedule", back_populates="location")

class Schedule(Base):
    __tablename__ = "schedules"

    schedule_id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False)
    location_id = Column(Integer, ForeignKey("pickup_locations.location_id"), nullable=False)
    pickup_start_time = Column(Time, nullable=False)
    pickup_end_time = Column(Time, nullable=False)
    status = Column(String(20), nullable=False, default="ACTIVE")
    create_time = Column(DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint('date', 'location_id', name='uix_date_location'),
    )

    # Relationships
    location = relationship("PickupLocation", back_populates="schedules")
    orders = relationship("Order", back_populates="schedule")
