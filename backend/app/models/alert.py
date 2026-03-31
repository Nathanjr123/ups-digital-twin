"""
Pydantic Models for Alerts
Defines data structures for alert management.
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Literal, Optional
from uuid import UUID, uuid4


class AlertBase(BaseModel):
    """Base alert information."""
    
    ups_id: str
    alert_type: Literal[
        "anomaly_detected",
        "failure_predicted",
        "high_temperature",
        "low_battery",
        "overload",
        "input_power_issue",
        "maintenance_required"
    ]
    severity: Literal["info", "warning", "high", "critical"]
    message: str
    details: Optional[str] = None


class Alert(AlertBase):
    """Complete alert with metadata."""
    
    alert_id: str = Field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = Field(default_factory=datetime.now)
    status: Literal["active", "acknowledged", "resolved"] = Field(default="active")
    acknowledged_at: Optional[datetime] = None
    acknowledged_by: Optional[str] = None
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[str] = None
    recommended_action: Optional[str] = None
    related_metrics: dict = Field(default_factory=dict)
    
    class Config:
        json_schema_extra = {
            "example": {
                "alert_id": "550e8400-e29b-41d4-a716-446655440000",
                "ups_id": "UPS-009",
                "alert_type": "failure_predicted",
                "severity": "critical",
                "message": "Battery failure predicted in 3 days",
                "details": "Battery SOC declining rapidly, temperature elevated",
                "timestamp": "2024-03-26T10:30:00",
                "status": "active",
                "recommended_action": "Schedule immediate battery replacement",
                "related_metrics": {
                    "battery_soc": 68.5,
                    "battery_temperature": 37.2,
                    "failure_probability": 0.92
                }
            }
        }


class AlertCreate(AlertBase):
    """Model for creating new alerts."""
    pass


class AlertUpdate(BaseModel):
    """Model for updating alerts."""
    
    status: Optional[Literal["active", "acknowledged", "resolved"]] = None
    acknowledged_by: Optional[str] = None
    resolved_by: Optional[str] = None


class AlertStats(BaseModel):
    """Alert statistics."""
    
    total_alerts: int
    active_alerts: int
    acknowledged_alerts: int
    resolved_alerts: int
    critical_alerts: int
    high_alerts: int
    warning_alerts: int
    info_alerts: int
    alerts_by_type: dict[str, int] = Field(default_factory=dict)
    alerts_by_ups: dict[str, int] = Field(default_factory=dict)
    
    class Config:
        json_schema_extra = {
            "example": {
                "total_alerts": 15,
                "active_alerts": 8,
                "acknowledged_alerts": 5,
                "resolved_alerts": 2,
                "critical_alerts": 2,
                "high_alerts": 3,
                "warning_alerts": 6,
                "info_alerts": 4,
                "alerts_by_type": {
                    "failure_predicted": 2,
                    "high_temperature": 4,
                    "anomaly_detected": 5
                },
                "alerts_by_ups": {
                    "UPS-009": 5,
                    "UPS-011": 3,
                    "UPS-012": 4
                }
            }
        }


class AlertList(BaseModel):
    """Paginated list of alerts."""
    
    alerts: list[Alert]
    total: int
    page: int = 1
    page_size: int = 50
    
    class Config:
        json_schema_extra = {
            "example": {
                "alerts": [],
                "total": 15,
                "page": 1,
                "page_size": 50
            }
        }
