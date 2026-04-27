from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import os, shutil, tempfile, statistics

from ..database import get_db
from ..models.user import User, UserRole
from ..models.traffic_record import TrafficRecord, CongestionLevel
from ..models.road import Road
from ..models.alert import Alert, AlertType, AlertSeverity
from ..schemas.traffic import TrafficRecordCreate, TrafficRecordResponse, TrafficDataUpload
from ..utils.dependencies import get_current_user, require_role
from ..config import settings

router = APIRouter()


def _estimate_speed_from_density(density: float) -> float:
    """Estimate average speed (km/h) from vehicle density when no optical flow is available."""
    if density <= 0.005:  return 75.0
    if density <= 0.01:   return 60.0
    if density <= 0.02:   return 45.0
    if density <= 0.03:   return 30.0
    if density <= 0.04:   return 18.0
    return 8.0


def _run_ml_pipeline(video_path: str, road: Road) -> dict:
    """Run full ML pipeline on a saved video file and return aggregated metrics."""
    from ..ml.vehicle_detection import VehicleDetector
    from ..ml.classification import CongestionClassifier

    detector   = VehicleDetector(
        model_path=settings.MODEL_PATH,
        confidence_threshold=settings.CONFIDENCE_THRESHOLD,
        nms_threshold=settings.NMS_THRESHOLD,
    )
    classifier = CongestionClassifier(
        density_low=settings.DENSITY_LOW / 1000,
        density_medium=settings.DENSITY_MEDIUM / 1000,
        density_high=settings.DENSITY_HIGH / 1000,
        speed_threshold_free=settings.SPEED_THRESHOLD_FREE,
        speed_threshold_moderate=settings.SPEED_THRESHOLD_MODERATE,
    )

    frame_results, unique_counts = detector.process_video(video_path, frame_skip=settings.FRAME_SKIP)

    if not frame_results:
        raise ValueError("No frames could be processed from the video.")

    # Unique counts = total distinct vehicles tracked across the entire video
    total       = unique_counts["total"]
    cars        = unique_counts["car"]
    trucks      = unique_counts["truck"]
    buses       = unique_counts["bus"]
    motorcycles = unique_counts["motorcycle"]

    # Peak concurrent vehicles (for density — how packed the road is at worst moment)
    all_counts = [f["counts"] for f in frame_results]
    peak_concurrent = max(c["total"] for c in all_counts)

    # Average confidence
    all_confs = [
        d["confidence"]
        for f in frame_results
        for d in f["detections"]
    ]
    avg_confidence = round(statistics.mean(all_confs), 3) if all_confs else 0.9

    # Density uses peak concurrent vehicles over camera view area (~500 m² default)
    area = road.area_sqm if road.area_sqm and road.area_sqm > 0 else 500.0
    density = round(peak_concurrent / area, 5)

    estimated_speed = _estimate_speed_from_density(density)
    level           = classifier.classify(density, total, estimated_speed)
    score           = classifier.get_score(density, estimated_speed)

    return {
        "vehicle_count":     total,
        "peak_concurrent":   peak_concurrent,
        "car_count":         cars,
        "truck_count":       trucks,
        "bus_count":         buses,
        "motorcycle_count":  motorcycles,
        "density":           density,
        "average_speed":     estimated_speed,
        "congestion_level":  level,
        "congestion_score":  score,
        "confidence":        avg_confidence,
        "frames_processed":  len(frame_results),
    }


@router.post("/upload-video")
async def upload_video(
    file: UploadFile = File(...),
    road_id: int = Form(...),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.AUTHORITY])),
    db: Session = Depends(get_db),
):
    """Upload CCTV footage, run YOLOv8 detection, and save a TrafficRecord."""

    # Validate file type
    allowed = {"video/mp4", "video/avi", "video/x-msvideo", "video/quicktime",
               "video/x-matroska", "video/webm"}
    if file.content_type not in allowed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type: {file.content_type}. Upload MP4, AVI, MOV, MKV or WebM.",
        )

    # Verify road exists
    road = db.query(Road).filter(Road.id == road_id).first()
    if not road:
        raise HTTPException(status_code=404, detail="Road not found")

    # Save uploaded file to a temp location
    os.makedirs(settings.VIDEO_UPLOAD_PATH, exist_ok=True)
    suffix = os.path.splitext(file.filename or "upload.mp4")[1] or ".mp4"
    tmp_path = os.path.join(settings.VIDEO_UPLOAD_PATH, f"upload_{road_id}_{int(datetime.utcnow().timestamp())}{suffix}")

    try:
        with open(tmp_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        # Run ML pipeline
        try:
            metrics = _run_ml_pipeline(tmp_path, road)
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Video processing failed: {str(exc)}",
            )

        # Save TrafficRecord
        now = datetime.utcnow()
        record = TrafficRecord(
            road_id=road.id,
            vehicle_count=metrics["vehicle_count"],
            car_count=metrics["car_count"],
            truck_count=metrics["truck_count"],
            bus_count=metrics["bus_count"],
            motorcycle_count=metrics["motorcycle_count"],
            density=metrics["density"],
            average_speed=metrics["average_speed"],
            congestion_level=metrics["congestion_level"],
            congestion_score=metrics["congestion_score"],
            timestamp=now,
            hour_of_day=now.hour,
            day_of_week=now.weekday(),
            source="video",
            source_file=os.path.basename(tmp_path),
            model_version="yolov8n",
            confidence=metrics["confidence"],
        )
        db.add(record)

        # Auto-create alert if congested/severe
        if metrics["congestion_level"] in (CongestionLevel.CONGESTED, CongestionLevel.SEVERE):
            severity = (AlertSeverity.CRITICAL
                        if metrics["congestion_level"] == CongestionLevel.SEVERE
                        else AlertSeverity.WARNING)
            alert = Alert(
                road_id=road.id,
                alert_type=AlertType.CONGESTION,
                severity=severity,
                title=f"High congestion detected on {road.name}",
                message=(f"Video analysis detected {metrics['vehicle_count']} vehicles. "
                         f"Congestion score: {metrics['congestion_score']:.1f}/100."),
                is_active=True,
                is_resolved=False,
            )
            db.add(alert)

        db.commit()
        db.refresh(record)

        return {
            "message": "Video processed successfully",
            "road_id": road.id,
            "road_name": road.name,
            "traffic_record_id": record.id,
            "frames_processed": metrics["frames_processed"],
            "vehicle_count": metrics["vehicle_count"],
            "peak_concurrent": metrics["peak_concurrent"],
            "congestion_level": metrics["congestion_level"].value,
            "congestion_score": metrics["congestion_score"],
            "average_speed": metrics["average_speed"],
        }

    finally:
        # Clean up temp file
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


@router.post("/live-feed", status_code=status.HTTP_201_CREATED)
async def register_live_feed(
    feed_data: TrafficDataUpload,
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.AUTHORITY])),
    db: Session = Depends(get_db),
):
    road = db.query(Road).filter(Road.id == feed_data.road_id).first()
    if not road:
        raise HTTPException(status_code=404, detail="Road not found")
    return {"message": "Live feed registered successfully", "road_id": feed_data.road_id, "status": "active"}


@router.post("/data", response_model=TrafficRecordResponse, status_code=status.HTTP_201_CREATED)
async def insert_traffic_data(
    traffic_data: TrafficRecordCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    road = db.query(Road).filter(Road.id == traffic_data.road_id).first()
    if not road:
        raise HTTPException(status_code=404, detail="Road not found")

    now = datetime.utcnow()
    record = TrafficRecord(
        **traffic_data.dict(),
        timestamp=now,
        hour_of_day=now.hour,
        day_of_week=now.weekday(),
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.get("/live/{road_id}", response_model=TrafficRecordResponse)
async def get_live_traffic(road_id: int, db: Session = Depends(get_db)):
    record = (
        db.query(TrafficRecord)
        .filter(TrafficRecord.road_id == road_id)
        .order_by(TrafficRecord.timestamp.desc())
        .first()
    )
    if not record:
        raise HTTPException(status_code=404, detail="No traffic data found for this road")
    return record


@router.get("/history/{road_id}", response_model=List[TrafficRecordResponse])
async def get_traffic_history(road_id: int, limit: int = 100, db: Session = Depends(get_db)):
    return (
        db.query(TrafficRecord)
        .filter(TrafficRecord.road_id == road_id)
        .order_by(TrafficRecord.timestamp.desc())
        .limit(limit)
        .all()
    )
