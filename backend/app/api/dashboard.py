from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Optional
from datetime import datetime, timedelta

from ..database import get_db
from ..models.traffic_record import TrafficRecord, CongestionLevel
from ..models.road import Road
from ..models.alert import Alert
from ..schemas.dashboard import (
    DashboardOverview,
    RoadTrafficData,
    TrendData,
    TrendDataPoint,
    HeatmapData,
    HeatmapPoint,
    PeakHoursResponse,
    PeakHourData,
    RoadComparison,
    CongestionStats
)

router = APIRouter()


@router.get("/overview", response_model=DashboardOverview)
async def get_dashboard_overview(db: Session = Depends(get_db)):
    """Get overall congestion summary"""

    # Get latest record for each road
    subquery = db.query(
        TrafficRecord.road_id,
        func.max(TrafficRecord.timestamp).label("max_timestamp")
    ).group_by(TrafficRecord.road_id).subquery()

    latest_records = db.query(TrafficRecord).join(
        subquery,
        (TrafficRecord.road_id == subquery.c.road_id) &
        (TrafficRecord.timestamp == subquery.c.max_timestamp)
    ).all()

    # Calculate congestion stats
    total_roads = db.query(Road).filter(Road.is_active == True).count()
    free_flow = sum(1 for r in latest_records if r.congestion_level == CongestionLevel.FREE_FLOW)
    moderate = sum(1 for r in latest_records if r.congestion_level == CongestionLevel.MODERATE)
    congested = sum(1 for r in latest_records if r.congestion_level == CongestionLevel.CONGESTED)
    severe = sum(1 for r in latest_records if r.congestion_level == CongestionLevel.SEVERE)

    # Total vehicles
    total_vehicles = sum(r.vehicle_count for r in latest_records)

    # Active alerts
    active_alerts = db.query(Alert).filter(
        Alert.is_active == True,
        Alert.is_resolved == False
    ).count()

    # Average speed
    speeds = [r.average_speed for r in latest_records if r.average_speed is not None]
    avg_speed = sum(speeds) / len(speeds) if speeds else None

    return DashboardOverview(
        congestion_stats=CongestionStats(
            total_roads=total_roads,
            free_flow=free_flow,
            moderate=moderate,
            congested=congested,
            severe=severe
        ),
        total_vehicles_detected=total_vehicles,
        active_alerts=active_alerts,
        last_updated=datetime.utcnow(),
        average_speed=avg_speed
    )


@router.get("/road/{road_id}", response_model=RoadTrafficData)
async def get_road_data(road_id: int, db: Session = Depends(get_db)):
    """Get road-specific traffic data"""

    road = db.query(Road).filter(Road.id == road_id).first()
    if not road:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Road not found"
        )

    # Get latest traffic record
    latest_record = db.query(TrafficRecord)\
        .filter(TrafficRecord.road_id == road_id)\
        .order_by(desc(TrafficRecord.timestamp))\
        .first()

    if not latest_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No traffic data available for this road"
        )

    return RoadTrafficData(
        road_id=road.id,
        road_name=road.name,
        road_code=road.road_code,
        current_congestion=latest_record.congestion_level,
        vehicle_count=latest_record.vehicle_count,
        average_speed=latest_record.average_speed,
        density=latest_record.density,
        last_updated=latest_record.timestamp,
        congestion_score=latest_record.congestion_score
    )


@router.get("/trends", response_model=TrendData)
async def get_trends(
    road_id: int,
    period: str = Query("hourly", regex="^(hourly|daily|weekly)$"),
    db: Session = Depends(get_db)
):
    """Get hourly/daily/weekly trends"""

    road = db.query(Road).filter(Road.id == road_id).first()
    if not road:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Road not found"
        )

    # Calculate time range based on period
    now = datetime.utcnow()
    if period == "hourly":
        start_time = now - timedelta(hours=24)
    elif period == "daily":
        start_time = now - timedelta(days=7)
    else:  # weekly
        start_time = now - timedelta(weeks=4)

    # Fetch records
    records = db.query(TrafficRecord)\
        .filter(
            TrafficRecord.road_id == road_id,
            TrafficRecord.timestamp >= start_time
        )\
        .order_by(TrafficRecord.timestamp)\
        .all()

    data_points = [
        TrendDataPoint(
            timestamp=record.timestamp,
            vehicle_count=record.vehicle_count,
            congestion_level=record.congestion_level,
            average_speed=record.average_speed
        )
        for record in records
    ]

    return TrendData(
        road_id=road_id,
        road_name=road.name,
        period=period,
        data_points=data_points
    )


@router.get("/heatmap", response_model=HeatmapData)
async def get_heatmap(db: Session = Depends(get_db)):
    """Get congestion heatmap data"""

    # Get latest record for each road
    subquery = db.query(
        TrafficRecord.road_id,
        func.max(TrafficRecord.timestamp).label("max_timestamp")
    ).group_by(TrafficRecord.road_id).subquery()

    latest_records = db.query(TrafficRecord, Road).join(
        Road, TrafficRecord.road_id == Road.id
    ).join(
        subquery,
        (TrafficRecord.road_id == subquery.c.road_id) &
        (TrafficRecord.timestamp == subquery.c.max_timestamp)
    ).all()

    points = [
        HeatmapPoint(
            road_id=road.id,
            road_name=road.name,
            road_code=road.road_code,
            latitude=road.latitude,
            longitude=road.longitude,
            congestion_score=record.congestion_score or 0,
            congestion_level=record.congestion_level
        )
        for record, road in latest_records
    ]

    return HeatmapData(
        timestamp=datetime.utcnow(),
        points=points
    )


@router.get("/alerts", response_model=List[dict])
async def get_active_alerts(db: Session = Depends(get_db)):
    """Get active congestion alerts"""

    alerts = db.query(Alert).filter(
        Alert.is_active == True,
        Alert.is_resolved == False
    ).order_by(desc(Alert.created_at)).all()

    return [
        {
            "id": alert.id,
            "road_id": alert.road_id,
            "alert_type": alert.alert_type.value,
            "severity": alert.severity.value,
            "title": alert.title,
            "message": alert.message,
            "created_at": alert.created_at
        }
        for alert in alerts
    ]


@router.get("/peak-hours", response_model=PeakHoursResponse)
async def get_peak_hours(
    road_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get peak hour analytics"""

    query = db.query(
        TrafficRecord.hour_of_day,
        TrafficRecord.day_of_week,
        func.avg(TrafficRecord.vehicle_count).label("avg_vehicles"),
        func.avg(TrafficRecord.congestion_score).label("avg_score")
    )

    if road_id:
        query = query.filter(TrafficRecord.road_id == road_id)

    peak_data = query.group_by(
        TrafficRecord.hour_of_day,
        TrafficRecord.day_of_week
    ).all()

    peak_hours = [
        PeakHourData(
            hour=data.hour_of_day,
            day_of_week=data.day_of_week,
            average_vehicle_count=float(data.avg_vehicles or 0),
            average_congestion_score=float(data.avg_score or 0),
            most_common_level=CongestionLevel.MODERATE  # TODO: Calculate actual mode
        )
        for data in peak_data
    ]

    # Sort by congestion score
    peak_hours.sort(key=lambda x: x.average_congestion_score, reverse=True)

    return PeakHoursResponse(
        road_id=road_id,
        peak_hours=peak_hours[:10]  # Top 10 peak hours
    )


@router.get("/comparison", response_model=RoadComparison)
async def compare_roads(
    road1_id: int,
    road2_id: int,
    hours: int = Query(24, ge=1, le=168),
    db: Session = Depends(get_db)
):
    """Compare two road segments"""

    road1 = db.query(Road).filter(Road.id == road1_id).first()
    road2 = db.query(Road).filter(Road.id == road2_id).first()

    if not road1 or not road2:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="One or both roads not found"
        )

    start_time = datetime.utcnow() - timedelta(hours=hours)

    # Get average stats for road 1
    road1_stats = db.query(
        func.avg(TrafficRecord.congestion_score).label("avg_congestion"),
        func.avg(TrafficRecord.vehicle_count).label("avg_vehicles")
    ).filter(
        TrafficRecord.road_id == road1_id,
        TrafficRecord.timestamp >= start_time
    ).first()

    # Get average stats for road 2
    road2_stats = db.query(
        func.avg(TrafficRecord.congestion_score).label("avg_congestion"),
        func.avg(TrafficRecord.vehicle_count).label("avg_vehicles")
    ).filter(
        TrafficRecord.road_id == road2_id,
        TrafficRecord.timestamp >= start_time
    ).first()

    return RoadComparison(
        road1_id=road1_id,
        road1_name=road1.name,
        road1_avg_congestion=float(road1_stats.avg_congestion or 0),
        road1_avg_vehicles=float(road1_stats.avg_vehicles or 0),
        road2_id=road2_id,
        road2_name=road2.name,
        road2_avg_congestion=float(road2_stats.avg_congestion or 0),
        road2_avg_vehicles=float(road2_stats.avg_vehicles or 0),
        time_period=f"Last {hours} hours"
    )
