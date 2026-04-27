from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from ..models.alert import AlertType, AlertSeverity


class AlertBase(BaseModel):
    """Base alert schema"""
    road_id: int
    alert_type: AlertType
    severity: AlertSeverity = AlertSeverity.INFO
    title: str = Field(..., max_length=255)
    message: Optional[str] = None


class AlertCreate(AlertBase):
    """Schema for creating an alert"""
    pass


class AlertUpdate(BaseModel):
    """Schema for updating an alert"""
    is_active: Optional[bool] = None
    is_resolved: Optional[bool] = None


class AlertResponse(AlertBase):
    """Schema for alert response"""
    id: int
    is_active: bool
    is_resolved: bool
    created_at: datetime
    resolved_at: Optional[datetime] = None

    class Config:
        from_attributes = True
