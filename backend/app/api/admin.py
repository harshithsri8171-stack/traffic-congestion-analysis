from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta
import random

from ..database import get_db
from ..models.user import User, UserRole
from ..models.road import Road
from ..models.traffic_record import TrafficRecord, CongestionLevel
from ..models.alert import Alert, AlertType, AlertSeverity
from ..schemas.road import RoadCreate, RoadUpdate, RoadResponse
from ..schemas.user import UserResponse
from ..utils.dependencies import require_role

router = APIRouter()


@router.post("/add-road", response_model=RoadResponse, status_code=status.HTTP_201_CREATED)
async def add_road(
    road_data: RoadCreate,
    current_user: User = Depends(require_role([UserRole.ADMIN])),
    db: Session = Depends(get_db)
):
    """Add a new road segment (Admin only)"""

    # Check if road code already exists
    existing_road = db.query(Road).filter(Road.road_code == road_data.road_code).first()
    if existing_road:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Road with this code already exists"
        )

    # Create new road
    new_road = Road(**road_data.dict())
    db.add(new_road)
    db.commit()
    db.refresh(new_road)

    return new_road


@router.put("/update-road/{road_id}", response_model=RoadResponse)
async def update_road(
    road_id: int,
    road_data: RoadUpdate,
    current_user: User = Depends(require_role([UserRole.ADMIN])),
    db: Session = Depends(get_db)
):
    """Update road segment (Admin only)"""

    road = db.query(Road).filter(Road.id == road_id).first()
    if not road:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Road not found"
        )

    # Update fields
    update_data = road_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(road, field, value)

    db.commit()
    db.refresh(road)

    return road


@router.delete("/delete-road/{road_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_road(
    road_id: int,
    current_user: User = Depends(require_role([UserRole.ADMIN])),
    db: Session = Depends(get_db)
):
    """Delete road segment (Admin only)"""

    road = db.query(Road).filter(Road.id == road_id).first()
    if not road:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Road not found"
        )

    db.delete(road)
    db.commit()

    return None


@router.get("/roads", response_model=List[RoadResponse])
async def list_roads(
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.AUTHORITY])),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 500,
    active_only: bool = True
):
    """List all roads (Admin/Authority)"""

    query = db.query(Road)

    if active_only:
        query = query.filter(Road.is_active == True)

    roads = query.offset(skip).limit(limit).all()
    return roads


@router.get("/users", response_model=List[UserResponse])
async def list_users(
    current_user: User = Depends(require_role([UserRole.ADMIN])),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    """List all users (Admin only)"""

    users = db.query(User).offset(skip).limit(limit).all()
    return users


@router.put("/users/{user_id}/toggle-active", response_model=UserResponse)
async def toggle_user_active(
    user_id: int,
    current_user: User = Depends(require_role([UserRole.ADMIN])),
    db: Session = Depends(get_db)
):
    """Toggle user active status (Admin only)"""

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    user.is_active = not user.is_active
    db.commit()
    db.refresh(user)

    return user


@router.post("/seed", status_code=status.HTTP_201_CREATED)
async def seed_demo_data(
    current_user: User = Depends(require_role([UserRole.ADMIN])),
    db: Session = Depends(get_db)
):
    """Seed sample roads and traffic records for demo/development."""

    SAMPLE_ROADS = [
        # Central / Tank Bund
        {"name": "Tank Bund Road",              "road_code": "HYD-001", "start_point": "NTR Garden",          "end_point": "Secretariat",           "latitude": 17.4126, "longitude": 78.4729, "length_km": 4.1, "lanes": 4, "road_type": "arterial",   "area_sqm": 8200},
        # Banjara Hills
        {"name": "Banjara Hills Road No.1",     "road_code": "HYD-002", "start_point": "Road No.1 Junction",  "end_point": "Jubilee Hills",          "latitude": 17.4157, "longitude": 78.4499, "length_km": 3.5, "lanes": 4, "road_type": "arterial",   "area_sqm": 7000},
        {"name": "Banjara Hills Road No.10",    "road_code": "HYD-020", "start_point": "Amrutha Castle",      "end_point": "Road No.12",             "latitude": 17.4200, "longitude": 78.4450, "length_km": 2.0, "lanes": 2, "road_type": "local",      "area_sqm": 3000},
        {"name": "Banjara Hills Road No.12",    "road_code": "HYD-021", "start_point": "GVK Mall",            "end_point": "Care Hospital",          "latitude": 17.4238, "longitude": 78.4468, "length_km": 2.4, "lanes": 4, "road_type": "arterial",   "area_sqm": 4800},
        # HITEC City / Madhapur / Gachibowli
        {"name": "Hitech City Main Road",       "road_code": "HYD-003", "start_point": "Madhapur Junction",   "end_point": "Hitech City Metro",      "latitude": 17.4474, "longitude": 78.3762, "length_km": 5.2, "lanes": 6, "road_type": "highway",    "area_sqm": 15600},
        {"name": "Gachibowli Flyover",          "road_code": "HYD-005", "start_point": "DLF Cyber City",      "end_point": "Outer Ring Road",        "latitude": 17.4399, "longitude": 78.3489, "length_km": 2.0, "lanes": 4, "road_type": "expressway", "area_sqm": 6000},
        {"name": "Madhapur Main Road",          "road_code": "HYD-022", "start_point": "Hitech City Metro",   "end_point": "Kondapur Junction",      "latitude": 17.4503, "longitude": 78.3913, "length_km": 3.8, "lanes": 4, "road_type": "arterial",   "area_sqm": 7600},
        {"name": "Kondapur Main Road",          "road_code": "HYD-023", "start_point": "Kondapur Junction",   "end_point": "KPHB Colony",            "latitude": 17.4648, "longitude": 78.3609, "length_km": 4.5, "lanes": 4, "road_type": "arterial",   "area_sqm": 9000},
        {"name": "Gachibowli – Nanakramguda",   "road_code": "HYD-024", "start_point": "ISB Road",            "end_point": "Nanakramguda Junction",  "latitude": 17.4280, "longitude": 78.3502, "length_km": 3.0, "lanes": 4, "road_type": "arterial",   "area_sqm": 6000},
        # Jubilee Hills / Film Nagar
        {"name": "Jubilee Hills Checkpost",     "road_code": "HYD-004", "start_point": "Film Nagar",          "end_point": "Panjagutta",             "latitude": 17.4311, "longitude": 78.4075, "length_km": 2.8, "lanes": 4, "road_type": "local",      "area_sqm": 5600},
        {"name": "Road No. 36, Jubilee Hills",  "road_code": "HYD-025", "start_point": "Kavuri Hills",        "end_point": "Madhapur",               "latitude": 17.4408, "longitude": 78.4053, "length_km": 2.2, "lanes": 2, "road_type": "local",      "area_sqm": 3300},
        # Secunderabad
        {"name": "Secunderabad Station Road",   "road_code": "HYD-006", "start_point": "Secunderabad Stn",    "end_point": "Paradise Circle",        "latitude": 17.4399, "longitude": 78.4983, "length_km": 1.8, "lanes": 2, "road_type": "local",      "area_sqm": 3600},
        {"name": "SP Road, Secunderabad",       "road_code": "HYD-026", "start_point": "Clock Tower",         "end_point": "Trimulgherry",           "latitude": 17.4462, "longitude": 78.5012, "length_km": 3.1, "lanes": 4, "road_type": "arterial",   "area_sqm": 6200},
        {"name": "MG Road, Secunderabad",       "road_code": "HYD-027", "start_point": "Paradise Circle",     "end_point": "Patny Centre",           "latitude": 17.4418, "longitude": 78.4940, "length_km": 2.5, "lanes": 4, "road_type": "arterial",   "area_sqm": 5000},
        # Ameerpet / Panjagutta
        {"name": "Ameerpet Main Road",          "road_code": "HYD-007", "start_point": "Ameerpet Metro",      "end_point": "Punjagutta Circle",      "latitude": 17.4375, "longitude": 78.4483, "length_km": 2.5, "lanes": 4, "road_type": "arterial",   "area_sqm": 5000},
        {"name": "Panjagutta Road",             "road_code": "HYD-028", "start_point": "Panjagutta Circle",   "end_point": "Somajiguda",             "latitude": 17.4314, "longitude": 78.4530, "length_km": 2.0, "lanes": 4, "road_type": "arterial",   "area_sqm": 4000},
        # Dilsukhnagar / LB Nagar
        {"name": "Dilsukhnagar Main Road",      "road_code": "HYD-008", "start_point": "Dilsukhnagar Metro",  "end_point": "Nagole",                 "latitude": 17.3688, "longitude": 78.5247, "length_km": 3.8, "lanes": 4, "road_type": "arterial",   "area_sqm": 7600},
        {"name": "LB Nagar Flyover",            "road_code": "HYD-009", "start_point": "LB Nagar Circle",     "end_point": "Meerpet",                "latitude": 17.3465, "longitude": 78.5476, "length_km": 2.2, "lanes": 4, "road_type": "expressway", "area_sqm": 4400},
        {"name": "Uppal Main Road",             "road_code": "HYD-029", "start_point": "Uppal Metro",         "end_point": "ECIL X Roads",           "latitude": 17.4053, "longitude": 78.5593, "length_km": 4.0, "lanes": 4, "road_type": "arterial",   "area_sqm": 8000},
        # Kukatpally / KPHB
        {"name": "Kukatpally Housing Board Rd", "road_code": "HYD-010", "start_point": "KPHB Phase 1",        "end_point": "JNTU Circle",            "latitude": 17.4947, "longitude": 78.3996, "length_km": 3.2, "lanes": 4, "road_type": "arterial",   "area_sqm": 6400},
        {"name": "JNTU – Miyapur Road",         "road_code": "HYD-030", "start_point": "JNTU Circle",         "end_point": "Miyapur Metro",          "latitude": 17.4958, "longitude": 78.3852, "length_km": 2.8, "lanes": 4, "road_type": "arterial",   "area_sqm": 5600},
        # Outer Ring Road
        {"name": "ORR – Gachibowli Stretch",    "road_code": "HYD-011", "start_point": "Gachibowli Exit",     "end_point": "Kokapet Exit",           "latitude": 17.4070, "longitude": 78.3308, "length_km": 8.5, "lanes": 8, "road_type": "expressway", "area_sqm": 34000},
        {"name": "ORR – Shamshabad Stretch",    "road_code": "HYD-012", "start_point": "Shamshabad Exit",     "end_point": "Tukkuguda Exit",         "latitude": 17.2543, "longitude": 78.4304, "length_km": 7.0, "lanes": 8, "road_type": "expressway", "area_sqm": 28000},
        {"name": "ORR – Patancheru Stretch",    "road_code": "HYD-031", "start_point": "Patancheru Exit",     "end_point": "Miyapur Exit",           "latitude": 17.5254, "longitude": 78.2629, "length_km": 9.0, "lanes": 8, "road_type": "expressway", "area_sqm": 36000},
        # Charminar / Old City
        {"name": "Charminar Road",              "road_code": "HYD-013", "start_point": "Charminar",           "end_point": "Afzalgunj",              "latitude": 17.3616, "longitude": 78.4747, "length_km": 2.5, "lanes": 2, "road_type": "local",      "area_sqm": 3750},
        {"name": "Abids – Koti Road",           "road_code": "HYD-014", "start_point": "Abids Circle",        "end_point": "Koti Women's College",   "latitude": 17.3859, "longitude": 78.4847, "length_km": 2.0, "lanes": 4, "road_type": "arterial",   "area_sqm": 4000},
        {"name": "Nampally Station Road",       "road_code": "HYD-032", "start_point": "Nampally Station",    "end_point": "Abids",                  "latitude": 17.3839, "longitude": 78.4743, "length_km": 1.5, "lanes": 4, "road_type": "arterial",   "area_sqm": 3000},
        # Begumpet / Airport Road
        {"name": "Begumpet Airport Road",       "road_code": "HYD-015", "start_point": "Begumpet Metro",      "end_point": "Old Airport Junction",   "latitude": 17.4473, "longitude": 78.4686, "length_km": 3.0, "lanes": 4, "road_type": "arterial",   "area_sqm": 6000},
        {"name": "Raj Bhavan Road",             "road_code": "HYD-033", "start_point": "Somajiguda",          "end_point": "Rajbhavan Junction",     "latitude": 17.4326, "longitude": 78.4606, "length_km": 2.0, "lanes": 4, "road_type": "arterial",   "area_sqm": 4000},
        # Miyapur / Bachupally
        {"name": "Miyapur Main Road",           "road_code": "HYD-016", "start_point": "Miyapur Metro",       "end_point": "Bachupally",             "latitude": 17.4961, "longitude": 78.3658, "length_km": 4.5, "lanes": 4, "road_type": "arterial",   "area_sqm": 9000},
        # Mehdipatnam / Tolichowki
        {"name": "Mehdipatnam Main Road",       "road_code": "HYD-017", "start_point": "Mehdipatnam Circle",  "end_point": "Tolichowki",             "latitude": 17.3938, "longitude": 78.4370, "length_km": 3.5, "lanes": 4, "road_type": "arterial",   "area_sqm": 7000},
        {"name": "Tolichowki – Attapur Road",   "road_code": "HYD-034", "start_point": "Tolichowki X Road",   "end_point": "Attapur",                "latitude": 17.3869, "longitude": 78.4200, "length_km": 3.0, "lanes": 4, "road_type": "arterial",   "area_sqm": 6000},
        # Nacharam / Habsiguda
        {"name": "Nacharam Main Road",          "road_code": "HYD-018", "start_point": "Nacharam Jn",         "end_point": "Mallapur",               "latitude": 17.3974, "longitude": 78.5607, "length_km": 2.8, "lanes": 2, "road_type": "local",      "area_sqm": 4200},
        {"name": "Habsiguda – Tarnaka Road",    "road_code": "HYD-035", "start_point": "Habsiguda",           "end_point": "Tarnaka Metro",          "latitude": 17.4099, "longitude": 78.5397, "length_km": 2.5, "lanes": 4, "road_type": "arterial",   "area_sqm": 5000},
        # Airport / Shamshabad
        {"name": "Rajiv Gandhi International Airport Rd", "road_code": "HYD-019", "start_point": "Mehdipatnam", "end_point": "RGIA Terminal",    "latitude": 17.2403, "longitude": 78.4294, "length_km": 22.0,"lanes": 6, "road_type": "highway",    "area_sqm": 66000},
        # Nallagandla / Tellapur
        {"name": "Nallagandla Main Road",       "road_code": "HYD-036", "start_point": "Nallagandla Circle",  "end_point": "Tellapur Junction",      "latitude": 17.4587, "longitude": 78.3178, "length_km": 4.0, "lanes": 4, "road_type": "arterial",   "area_sqm": 8000},
        # Kompally / Medchal Road
        {"name": "Kompally – Medchal Road",     "road_code": "HYD-037", "start_point": "Kompally",            "end_point": "Medchal",                "latitude": 17.5612, "longitude": 78.4882, "length_km": 8.0, "lanes": 4, "road_type": "highway",    "area_sqm": 16000},
        # Shamirpet
        {"name": "Shamirpet Lake Road",         "road_code": "HYD-038", "start_point": "Shamirpet Circle",    "end_point": "HMDA Lake",              "latitude": 17.5702, "longitude": 78.5406, "length_km": 5.0, "lanes": 2, "road_type": "local",      "area_sqm": 7500},
    ]

    CONGESTION_SEQUENCE = [
        CongestionLevel.FREE_FLOW, CongestionLevel.FREE_FLOW,
        CongestionLevel.MODERATE,  CongestionLevel.MODERATE,
        CongestionLevel.CONGESTED, CongestionLevel.SEVERE,
        CongestionLevel.CONGESTED, CongestionLevel.MODERATE,
        CongestionLevel.FREE_FLOW, CongestionLevel.FREE_FLOW,
        CongestionLevel.MODERATE,  CongestionLevel.CONGESTED,
    ]

    SCORE_MAP = {
        CongestionLevel.FREE_FLOW: (5.0,  25.0),
        CongestionLevel.MODERATE:  (30.0, 55.0),
        CongestionLevel.CONGESTED: (60.0, 78.0),
        CongestionLevel.SEVERE:    (80.0, 98.0),
    }

    SPEED_MAP = {
        CongestionLevel.FREE_FLOW: (55.0, 80.0),
        CongestionLevel.MODERATE:  (30.0, 50.0),
        CongestionLevel.CONGESTED: (15.0, 28.0),
        CongestionLevel.SEVERE:    (5.0,  14.0),
    }

    created_roads = 0
    created_records = 0

    for road_data in SAMPLE_ROADS:
        road = db.query(Road).filter(Road.road_code == road_data["road_code"]).first()
        if not road:
            road = Road(**road_data, is_active=True)
            db.add(road)
            db.flush()
            created_roads += 1

        # Create 24 hourly traffic records for the past 24 hours
        for h in range(24):
            ts = datetime.utcnow() - timedelta(hours=24 - h)
            level = CONGESTION_SEQUENCE[h % len(CONGESTION_SEQUENCE)]
            score_min, score_max = SCORE_MAP[level]
            speed_min, speed_max = SPEED_MAP[level]
            score = random.uniform(score_min, score_max)
            speed = random.uniform(speed_min, speed_max)
            vehicles = int(score * random.uniform(1.5, 3.5))

            record = TrafficRecord(
                road_id=road.id,
                vehicle_count=vehicles,
                car_count=int(vehicles * 0.65),
                truck_count=int(vehicles * 0.10),
                bus_count=int(vehicles * 0.08),
                motorcycle_count=int(vehicles * 0.17),
                density=round(score / 100, 3),
                average_speed=round(speed, 1),
                congestion_level=level,
                congestion_score=round(score, 2),
                timestamp=ts,
                hour_of_day=ts.hour,
                day_of_week=ts.weekday(),
                source="seed",
                confidence=0.92,
            )
            db.add(record)
            created_records += 1

        # Add one alert for congested/severe roads
        latest_level = CONGESTION_SEQUENCE[0]
        if latest_level in (CongestionLevel.CONGESTED, CongestionLevel.SEVERE):
            existing_alert = db.query(Alert).filter(
                Alert.road_id == road.id, Alert.is_active == True
            ).first()
            if not existing_alert:
                alert = Alert(
                    road_id=road.id,
                    alert_type=AlertType.CONGESTION,
                    severity=AlertSeverity.WARNING if latest_level == CongestionLevel.CONGESTED else AlertSeverity.CRITICAL,
                    title=f"High congestion on {road.name}",
                    message=f"Congestion score exceeds threshold. Consider alternate routes.",
                    is_active=True,
                    is_resolved=False,
                )
                db.add(alert)

    db.commit()
    return {
        "message": "Demo data seeded successfully",
        "roads_created": created_roads,
        "records_created": created_records,
    }
