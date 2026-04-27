from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime
from ..models.traffic_record import CongestionLevel


class CongestionStats(BaseModel):
    """Congestion statistics"""
    total_roads: int
    free_flow: int
    moderate: int
    congested: int
    severe: int


class DashboardOverview(BaseModel):
    """Dashboard overview response"""
    congestion_stats: CongestionStats
    total_vehicles_detected: int
    active_alerts: int
    last_updated: datetime
    average_speed: Optional[float] = None


class RoadTrafficData(BaseModel):
    """Road-specific traffic data"""
    road_id: int
    road_name: str
    road_code: str
    current_congestion: CongestionLevel
    vehicle_count: int
    average_speed: Optional[float] = None
    density: Optional[float] = None
    last_updated: datetime
    congestion_score: Optional[float] = None


class TrendDataPoint(BaseModel):
    """Single data point in trend analysis"""
    timestamp: datetime
    vehicle_count: int
    congestion_level: CongestionLevel
    average_speed: Optional[float] = None


class TrendData(BaseModel):
    """Trend data response"""
    road_id: int
    road_name: str
    period: str  # hourly, daily, weekly
    data_points: List[TrendDataPoint]


class HeatmapPoint(BaseModel):
    """Heatmap data point"""
    road_id: int
    road_name: str
    road_code: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    congestion_score: float
    congestion_level: CongestionLevel


class HeatmapData(BaseModel):
    """Heatmap response"""
    timestamp: datetime
    points: List[HeatmapPoint]


class PeakHourData(BaseModel):
    """Peak hour analysis"""
    hour: int  # 0-23
    day_of_week: int  # 0-6
    average_vehicle_count: float
    average_congestion_score: float
    most_common_level: CongestionLevel


class PeakHoursResponse(BaseModel):
    """Peak hours response"""
    road_id: Optional[int] = None
    peak_hours: List[PeakHourData]


class RoadComparison(BaseModel):
    """Compare two road segments"""
    road1_id: int
    road1_name: str
    road1_avg_congestion: float
    road1_avg_vehicles: float
    road2_id: int
    road2_name: str
    road2_avg_congestion: float
    road2_avg_vehicles: float
    time_period: str
