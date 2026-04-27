import cv2
import numpy as np
from ultralytics import YOLO
from typing import List, Dict, Tuple, Optional
import os


class VehicleDetector:
    """Detect and track vehicles using YOLOv8 with ByteTrack."""

    VEHICLE_CLASSES = {
        2: 'car',
        3: 'motorcycle',
        5: 'bus',
        7: 'truck'
    }

    def __init__(
        self,
        model_path: str = "yolov8n.pt",
        confidence_threshold: float = 0.5,
        nms_threshold: float = 0.4
    ):
        self.confidence_threshold = confidence_threshold
        self.nms_threshold = nms_threshold
        self.model = YOLO(model_path if os.path.exists(model_path) else "yolov8n.pt")

    def process_video(
        self,
        video_path: str,
        output_path: Optional[str] = None,
        frame_skip: int = 5,
    ) -> Tuple[List[Dict], Dict[str, int]]:
        """
        Process video with tracking.

        Returns:
            frame_results: per-sampled-frame detection snapshots
            unique_counts: total distinct vehicles seen across the whole video
        """
        cap = cv2.VideoCapture(video_path)
        frame_results: List[Dict] = []

        fps    = cap.get(cv2.CAP_PROP_FPS) or 25
        width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        writer = None
        if output_path:
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            writer = cv2.VideoWriter(output_path, fourcc, int(fps), (width, height))

        # Sets of unique track IDs per vehicle class
        seen_ids: Dict[str, set] = {c: set() for c in self.VEHICLE_CLASSES.values()}
        frame_count = 0

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            if frame_count % frame_skip == 0:
                results = self.model.track(
                    frame,
                    persist=True,
                    conf=self.confidence_threshold,
                    iou=self.nms_threshold,
                    verbose=False,
                    tracker="bytetrack.yaml",
                )

                detections: List[Dict] = []
                counts = {'car': 0, 'motorcycle': 0, 'bus': 0, 'truck': 0, 'total': 0}

                for result in results:
                    boxes = result.boxes
                    if boxes is None or boxes.id is None:
                        # Fall back to plain detection if tracker has no IDs yet
                        for box in boxes or []:
                            cid = int(box.cls[0])
                            if cid not in self.VEHICLE_CLASSES:
                                continue
                            cname = self.VEHICLE_CLASSES[cid]
                            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                            detections.append({
                                'class_id': cid,
                                'class_name': cname,
                                'track_id': None,
                                'bbox': [int(x1), int(y1), int(x2), int(y2)],
                                'confidence': float(box.conf[0]),
                            })
                            counts[cname] += 1
                            counts['total'] += 1
                        continue

                    for box, tid in zip(boxes, boxes.id):
                        cid = int(box.cls[0])
                        if cid not in self.VEHICLE_CLASSES:
                            continue
                        cname = self.VEHICLE_CLASSES[cid]
                        track_id = int(tid)
                        seen_ids[cname].add(track_id)
                        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                        detections.append({
                            'class_id': cid,
                            'class_name': cname,
                            'track_id': track_id,
                            'bbox': [int(x1), int(y1), int(x2), int(y2)],
                            'confidence': float(box.conf[0]),
                        })
                        counts[cname] += 1
                        counts['total'] += 1

                frame_results.append({
                    'frame_number': frame_count,
                    'detections': detections,
                    'counts': counts,
                })

                if writer:
                    writer.write(self._draw(frame, detections))

            frame_count += 1

        cap.release()
        if writer:
            writer.release()

        unique_counts = {k: len(v) for k, v in seen_ids.items()}
        unique_counts['total'] = sum(unique_counts.values())

        return frame_results, unique_counts

    # ------------------------------------------------------------------
    # Legacy helpers (kept for compatibility)
    # ------------------------------------------------------------------

    def detect_vehicles(self, frame: np.ndarray) -> List[Dict]:
        results = self.model(frame, conf=self.confidence_threshold, iou=self.nms_threshold)
        detections = []
        for result in results:
            for box in result.boxes:
                cid = int(box.cls[0])
                if cid in self.VEHICLE_CLASSES:
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    detections.append({
                        'class_id': cid,
                        'class_name': self.VEHICLE_CLASSES[cid],
                        'bbox': [int(x1), int(y1), int(x2), int(y2)],
                        'confidence': float(box.conf[0]),
                    })
        return detections

    def count_vehicles(self, detections: List[Dict]) -> Dict[str, int]:
        counts = {'car': 0, 'motorcycle': 0, 'bus': 0, 'truck': 0, 'total': 0}
        for d in detections:
            counts[d['class_name']] += 1
            counts['total'] += 1
        return counts

    def _draw(self, frame: np.ndarray, detections: List[Dict]) -> np.ndarray:
        colors = {'car': (0, 255, 0), 'motorcycle': (255, 0, 0),
                  'bus': (0, 0, 255), 'truck': (255, 255, 0)}
        out = frame.copy()
        for d in detections:
            x1, y1, x2, y2 = d['bbox']
            color = colors.get(d['class_name'], (255, 255, 255))
            cv2.rectangle(out, (x1, y1), (x2, y2), color, 2)
            label = f"{d['class_name']} #{d.get('track_id','?')}: {d['confidence']:.2f}"
            cv2.putText(out, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 1)
        return out

    # Keep old name for any external callers
    def draw_detections(self, frame, detections):
        return self._draw(frame, detections)
