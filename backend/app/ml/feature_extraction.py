import numpy as np
from typing import List, Dict, Optional


class FeatureExtractor:
    """Extract traffic features from vehicle detections"""

    def __init__(
        self,
        road_area_sqm: float = 1000.0,
        road_length_m: float = 100.0
    ):
        """
        Initialize feature extractor

        Args:
            road_area_sqm: Road area in square meters
            road_length_m: Road length in meters
        """
        self.road_area_sqm = road_area_sqm
        self.road_length_m = road_length_m

    def calculate_density(self, vehicle_count: int) -> float:
        """
        Calculate traffic density (vehicles per square meter)

        Args:
            vehicle_count: Number of vehicles detected

        Returns:
            Traffic density
        """
        if self.road_area_sqm <= 0:
            return 0.0

        return vehicle_count / self.road_area_sqm

    def estimate_speed(
        self,
        detections_t1: List[Dict],
        detections_t2: List[Dict],
        time_delta_sec: float
    ) -> Optional[float]:
        """
        Estimate average vehicle speed using optical flow or tracking
        (Simplified version - actual implementation would use tracking)

        Args:
            detections_t1: Detections at time t1
            detections_t2: Detections at time t2
            time_delta_sec: Time difference in seconds

        Returns:
            Estimated average speed in km/h
        """
        # Simplified speed estimation
        # In production, you'd use proper vehicle tracking (SORT, DeepSORT, etc.)

        if not detections_t1 or not detections_t2 or time_delta_sec <= 0:
            return None

        # Calculate average displacement (simplified)
        displacements = []

        for det1 in detections_t1:
            bbox1 = det1['bbox']
            center1 = ((bbox1[0] + bbox1[2]) / 2, (bbox1[1] + bbox1[3]) / 2)

            # Find closest detection in t2
            min_dist = float('inf')
            for det2 in detections_t2:
                bbox2 = det2['bbox']
                center2 = ((bbox2[0] + bbox2[2]) / 2, (bbox2[1] + bbox2[3]) / 2)

                dist = np.sqrt(
                    (center2[0] - center1[0])**2 +
                    (center2[1] - center1[1])**2
                )

                if dist < min_dist:
                    min_dist = dist

            if min_dist < 200:  # Only consider if reasonable
                displacements.append(min_dist)

        if not displacements:
            return None

        # Convert pixel displacement to meters (rough estimation)
        # This would need calibration based on camera setup
        pixels_to_meters = 0.1  # Example: 1 pixel = 0.1 meters
        avg_displacement_m = np.mean(displacements) * pixels_to_meters

        # Calculate speed in m/s then convert to km/h
        speed_ms = avg_displacement_m / time_delta_sec
        speed_kmh = speed_ms * 3.6

        # Cap at reasonable values
        return min(speed_kmh, 120.0)

    def extract_features(
        self,
        vehicle_counts: Dict[str, int],
        estimated_speed: Optional[float] = None
    ) -> Dict:
        """
        Extract all traffic features

        Args:
            vehicle_counts: Dictionary with vehicle counts
            estimated_speed: Estimated average speed in km/h

        Returns:
            Dictionary of extracted features
        """
        total_vehicles = vehicle_counts.get('total', 0)
        density = self.calculate_density(total_vehicles)

        features = {
            'vehicle_count': total_vehicles,
            'car_count': vehicle_counts.get('car', 0),
            'truck_count': vehicle_counts.get('truck', 0),
            'bus_count': vehicle_counts.get('bus', 0),
            'motorcycle_count': vehicle_counts.get('motorcycle', 0),
            'density': density,
            'average_speed': estimated_speed
        }

        return features

    def calculate_congestion_score(
        self,
        density: float,
        average_speed: Optional[float] = None,
        vehicle_count: int = 0
    ) -> float:
        """
        Calculate congestion score (0-100)

        Args:
            density: Traffic density
            average_speed: Average speed in km/h
            vehicle_count: Total vehicle count

        Returns:
            Congestion score between 0 and 100
        """
        # Base score from density
        # Normalize density to 0-50 range
        density_score = min(density * 100, 50)

        # Speed component (0-50)
        speed_score = 0
        if average_speed is not None:
            # Lower speed = higher congestion
            if average_speed >= 60:
                speed_score = 0
            elif average_speed >= 40:
                speed_score = 20
            elif average_speed >= 20:
                speed_score = 35
            else:
                speed_score = 50

        # Vehicle count component (small bonus)
        count_score = min(vehicle_count / 2, 10)

        total_score = density_score + speed_score + count_score
        return min(total_score, 100.0)
