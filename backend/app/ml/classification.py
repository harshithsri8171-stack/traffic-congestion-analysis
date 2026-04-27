from typing import Dict
from ..models.traffic_record import CongestionLevel


class CongestionClassifier:
    """Classify traffic congestion levels"""

    def __init__(
        self,
        density_low: float = 0.01,
        density_medium: float = 0.025,
        density_high: float = 0.04,
        speed_threshold_free: float = 50.0,
        speed_threshold_moderate: float = 30.0
    ):
        """
        Initialize congestion classifier

        Args:
            density_low: Low density threshold (vehicles/sqm)
            density_medium: Medium density threshold
            density_high: High density threshold
            speed_threshold_free: Speed threshold for free flow (km/h)
            speed_threshold_moderate: Speed threshold for moderate congestion (km/h)
        """
        self.density_low = density_low
        self.density_medium = density_medium
        self.density_high = density_high
        self.speed_threshold_free = speed_threshold_free
        self.speed_threshold_moderate = speed_threshold_moderate

    def classify_by_density(self, density: float) -> CongestionLevel:
        """
        Classify congestion based on density alone

        Args:
            density: Traffic density

        Returns:
            Congestion level
        """
        if density < self.density_low:
            return CongestionLevel.FREE_FLOW
        elif density < self.density_medium:
            return CongestionLevel.MODERATE
        elif density < self.density_high:
            return CongestionLevel.CONGESTED
        else:
            return CongestionLevel.SEVERE

    def classify_by_speed(self, speed: float) -> CongestionLevel:
        """
        Classify congestion based on speed alone

        Args:
            speed: Average speed in km/h

        Returns:
            Congestion level
        """
        if speed >= self.speed_threshold_free:
            return CongestionLevel.FREE_FLOW
        elif speed >= self.speed_threshold_moderate:
            return CongestionLevel.MODERATE
        elif speed >= 10.0:
            return CongestionLevel.CONGESTED
        else:
            return CongestionLevel.SEVERE

    def classify(
        self,
        density: float,
        vehicle_count: int,
        average_speed: float = None
    ) -> CongestionLevel:
        """
        Classify congestion level using multiple factors

        Args:
            density: Traffic density
            vehicle_count: Total vehicle count
            average_speed: Average speed in km/h (optional)

        Returns:
            Congestion level
        """
        # Start with density-based classification
        density_level = self.classify_by_density(density)

        # If speed is available, combine both factors
        if average_speed is not None:
            speed_level = self.classify_by_speed(average_speed)

            # Use the worse (higher) congestion level
            level_values = {
                CongestionLevel.FREE_FLOW: 0,
                CongestionLevel.MODERATE: 1,
                CongestionLevel.CONGESTED: 2,
                CongestionLevel.SEVERE: 3
            }

            density_value = level_values[density_level]
            speed_value = level_values[speed_level]

            # Take weighted average (60% speed, 40% density)
            combined_value = int(0.6 * speed_value + 0.4 * density_value)

            # Map back to congestion level
            value_to_level = {
                0: CongestionLevel.FREE_FLOW,
                1: CongestionLevel.MODERATE,
                2: CongestionLevel.CONGESTED,
                3: CongestionLevel.SEVERE
            }

            return value_to_level[combined_value]

        # Otherwise, use density-based classification
        return density_level

    def get_score(self, density: float, average_speed: float = None) -> float:
        """Return a 0-100 congestion score."""
        # Normalise density to 0-100 (cap at density_high * 2)
        density_score = min(density / (self.density_high * 2), 1.0) * 100

        if average_speed is not None:
            # Normalise speed inversely (0 km/h = 100, speed_free = 0)
            speed_score = max(0.0, 1.0 - (average_speed / self.speed_threshold_free)) * 100
            return round(0.6 * speed_score + 0.4 * density_score, 2)

        return round(density_score, 2)

    def get_recommendations(self, congestion_level: CongestionLevel) -> Dict[str, str]:
        """
        Get recommendations based on congestion level

        Args:
            congestion_level: Current congestion level

        Returns:
            Dictionary with recommendations
        """
        recommendations = {
            CongestionLevel.FREE_FLOW: {
                "status": "Good",
                "message": "Traffic is flowing smoothly",
                "action": "No action needed"
            },
            CongestionLevel.MODERATE: {
                "status": "Moderate",
                "message": "Traffic is moderate, slight delays expected",
                "action": "Consider alternative routes during peak hours"
            },
            CongestionLevel.CONGESTED: {
                "status": "Congested",
                "message": "Heavy traffic, significant delays expected",
                "action": "Use alternative routes, adjust signal timings"
            },
            CongestionLevel.SEVERE: {
                "status": "Severe",
                "message": "Severe congestion, major delays",
                "action": "Implement traffic control measures, redirect traffic"
            }
        }

        return recommendations.get(congestion_level, {})
