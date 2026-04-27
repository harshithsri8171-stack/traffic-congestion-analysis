from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from ..database import Base


class AlertSeverity(enum.Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class AlertType(enum.Enum):
    """Alert types"""
    CONGESTION = "congestion"
    ACCIDENT = "accident"
    SLOW_TRAFFIC = "slow_traffic"
    HIGH_DENSITY = "high_density"


class Alert(Base):
    """Traffic alert model"""
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    road_id = Column(Integer, ForeignKey("roads.id", ondelete="CASCADE"), nullable=False, index=True)

    # Alert details
    alert_type = Column(SQLEnum(AlertType), nullable=False)
    severity = Column(SQLEnum(AlertSeverity), default=AlertSeverity.INFO)
    title = Column(String(255), nullable=False)
    message = Column(Text)

    # Status
    is_active = Column(Boolean, default=True, index=True)
    is_resolved = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    resolved_at = Column(DateTime(timezone=True))

    # Relationships
    road = relationship("Road", back_populates="alerts")

    def __repr__(self):
        return f"<Alert {self.alert_type.value} on road_id={self.road_id} ({self.severity.value})>"
