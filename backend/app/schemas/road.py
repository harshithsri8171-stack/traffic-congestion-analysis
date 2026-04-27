from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class RoadBase(BaseModel):
    """Base road schema"""
    name: str = Field(..., max_length=255)
    road_code: str = Field(..., max_length=50)
    start_point: Optional[str] = None
    end_point: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    length_km: Optional[float] = Field(None, gt=0)
    lanes: int = Field(2, ge=1, le=10)
    road_type: Optional[str] = None
    area_sqm: Optional[float] = Field(None, gt=0)
    description: Optional[str] = None


class RoadCreate(RoadBase):
    """Schema for creating a road"""
    pass


class RoadUpdate(BaseModel):
    """Schema for updating a road"""
    name: Optional[str] = None
    start_point: Optional[str] = None
    end_point: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    length_km: Optional[float] = None
    lanes: Optional[int] = None
    road_type: Optional[str] = None
    area_sqm: Optional[float] = None
    is_active: Optional[bool] = None
    description: Optional[str] = None


class RoadResponse(RoadBase):
    """Schema for road response"""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
