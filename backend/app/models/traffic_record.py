from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum as SQLEnum, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from ..database import Base


class CongestionLevel(enum.Enum):
    """Traffic congestion levels"""
    FREE_FLOW = "free_flow"
    MODERATE = "moderate"
    CONGESTED = "congested"
    SEVERE = "severe"


class TrafficRecord(Base):
    """Traffic record model - stores processed traffic data"""
    __tablename__ = "traffic_records"

    id = Column(Integer, primary_key=True, index=True)
    road_id = Column(Integer, ForeignKey("roads.id", ondelete="CASCADE"), nullable=False, index=True)

    # Vehicle counts
    vehicle_count = Column(Integer, default=0)
    car_count = Column(Integer, default=0)
    truck_count = Column(Integer, default=0)
    bus_count = Column(Integer, default=0)
    motorcycle_count = Column(Integer, default=0)

    # Traffic metrics
    density = Column(Float)  # vehicles per unit area
    average_speed = Column(Float)  # km/h
    congestion_level = Column(SQLEnum(CongestionLevel), nullable=False)
    congestion_score = Column(Float)  # 0-100 score

    # Time information
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    hour_of_day = Column(Integer)  # 0-23
    day_of_week = Column(Integer)  # 0-6 (Monday=0)

    # Data source
    source = Column(String(50))  # video, live_feed, api, etc.
    source_file = Column(String(255))  # video filename if applicable

    # ML model info
    model_version = Column(String(50))
    confidence = Column(Float)  # average detection confidence

    # Additional metadata
    extra_data = Column(JSON)  # flexible field for additional data

    # Relationships
    road = relationship("Road", back_populates="traffic_records")

    def __repr__(self):
        return f"<TrafficRecord road_id={self.road_id} {self.congestion_level.value} at {self.timestamp}>"
