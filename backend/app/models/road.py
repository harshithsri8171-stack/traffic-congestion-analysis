from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from ..database import Base


class Road(Base):
    """Road segment model"""
    __tablename__ = "roads"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    road_code = Column(String(50), unique=True, nullable=False, index=True)

    # Location details
    start_point = Column(String(255))
    end_point = Column(String(255))
    latitude = Column(Float)
    longitude = Column(Float)

    # Road characteristics
    length_km = Column(Float)
    lanes = Column(Integer, default=2)
    road_type = Column(String(50))  # highway, arterial, local, etc.
    area_sqm = Column(Float)  # Road area for density calculation

    # Status
    is_active = Column(Boolean, default=True)
    description = Column(Text)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    traffic_records = relationship("TrafficRecord", back_populates="road", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="road", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Road {self.road_code}: {self.name}>"
