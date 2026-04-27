from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from ..models.traffic_record import CongestionLevel


class TrafficRecordBase(BaseModel):
    """Base traffic record schema"""
    road_id: int
    vehicle_count: int = Field(0, ge=0)
    car_count: int = Field(0, ge=0)
    truck_count: int = Field(0, ge=0)
    bus_count: int = Field(0, ge=0)
    motorcycle_count: int = Field(0, ge=0)
    density: Optional[float] = Field(None, ge=0)
    average_speed: Optional[float] = Field(None, ge=0)
    congestion_level: CongestionLevel


class TrafficRecordCreate(TrafficRecordBase):
    """Schema for creating a traffic record"""
    congestion_score: Optional[float] = Field(None, ge=0, le=100)
    source: Optional[str] = "manual"
    source_file: Optional[str] = None
    model_version: Optional[str] = None
    confidence: Optional[float] = Field(None, ge=0, le=1)
    metadata: Optional[Dict[str, Any]] = None


class TrafficRecordResponse(TrafficRecordBase):
    """Schema for traffic record response"""
    id: int
    congestion_score: Optional[float] = None
    timestamp: datetime
    hour_of_day: Optional[int] = None
    day_of_week: Optional[int] = None
    source: Optional[str] = None
    model_version: Optional[str] = None
    confidence: Optional[float] = None

    class Config:
        from_attributes = True


class TrafficDataUpload(BaseModel):
    """Schema for uploading traffic data"""
    road_id: int
    video_url: Optional[str] = None
    live_feed_url: Optional[str] = None
    process_immediately: bool = True
