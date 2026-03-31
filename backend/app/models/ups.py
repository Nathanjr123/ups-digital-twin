"""
Pydantic Models for UPS Data
Defines data structures and validation for UPS telemetry and metadata.
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Literal


class UPSTelemetry(BaseModel):
    """Real-time UPS telemetry data."""
    
    ups_id: str = Field(..., description="Unique UPS identifier")
    timestamp: datetime
    
    # Input power
    input_voltage: float = Field(..., ge=0, le=500, description="Input voltage (V)")
    input_current: float = Field(..., ge=0, description="Input current (A)")
    input_frequency: float = Field(..., ge=45, le=65, description="Input frequency (Hz)")
    
    # Output power
    output_voltage: float = Field(..., ge=0, le=500, description="Output voltage (V)")
    output_current: float = Field(..., ge=0, description="Output current (A)")
    output_frequency: float = Field(..., ge=45, le=65, description="Output frequency (Hz)")
    
    # Battery
    battery_voltage: float = Field(..., ge=0, description="Battery voltage (V)")
    battery_current: float = Field(..., description="Battery current (A), negative = charging")
    battery_soc: float = Field(..., ge=0, le=100, description="Battery state of charge (%)")
    battery_temperature: float = Field(..., description="Battery temperature (°C)")
    runtime_remaining: int = Field(..., ge=0, description="Estimated runtime remaining (minutes)")
    
    # System
    load_percentage: float = Field(..., ge=0, le=100, description="Load percentage (%)")
    inverter_temperature: float = Field(..., description="Inverter temperature (°C)")
    ambient_temperature: float = Field(..., description="Ambient temperature (°C)")
    
    # Status
    health_score: float = Field(..., ge=0, le=100, description="Overall health score")
    status: Literal["normal", "warning", "critical", "anomaly_detected", "failure"] = Field(..., description="Current status")
    on_battery: bool = Field(False, description="Running on battery power")
    
    class Config:
        json_schema_extra = {
            "example": {
                "ups_id": "UPS-001",
                "timestamp": "2024-03-26T10:30:00",
                "input_voltage": 230.5,
                "input_current": 12.3,
                "input_frequency": 50.0,
                "output_voltage": 230.0,
                "output_current": 12.0,
                "output_frequency": 50.0,
                "battery_voltage": 52.0,
                "battery_current": -2.5,
                "battery_soc": 95.0,
                "battery_temperature": 25.0,
                "runtime_remaining": 120,
                "load_percentage": 55.0,
                "inverter_temperature": 40.0,
                "ambient_temperature": 23.0,
                "health_score": 98.0,
                "status": "normal",
                "on_battery": False
            }
        }


class UPSMetadata(BaseModel):
    """UPS metadata and configuration."""
    
    ups_id: str
    location: str = Field(..., description="Physical location")
    model: str = Field(..., description="UPS model")
    installation_date: datetime
    last_maintenance: datetime
    capacity_kva: Optional[float] = Field(None, description="Rated capacity (kVA)")
    serial_number: Optional[str] = None
    firmware_version: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "ups_id": "UPS-001",
                "location": "Building A - Server Room",
                "model": "PowerGuard 10kVA",
                "installation_date": "2022-01-15T00:00:00",
                "last_maintenance": "2024-01-20T00:00:00",
                "capacity_kva": 10.0,
                "serial_number": "PG10K-2022-001",
                "firmware_version": "v2.3.1"
            }
        }


class UPSInfo(BaseModel):
    """Complete UPS information including metadata and latest telemetry."""
    
    metadata: UPSMetadata
    latest_telemetry: UPSTelemetry
    health_status: Literal["healthy", "warning", "critical"] = Field(..., description="Overall health classification")
    
    class Config:
        json_schema_extra = {
            "example": {
                "metadata": {
                    "ups_id": "UPS-001",
                    "location": "Building A - Server Room",
                    "model": "PowerGuard 10kVA",
                    "installation_date": "2022-01-15T00:00:00",
                    "last_maintenance": "2024-01-20T00:00:00"
                },
                "latest_telemetry": {
                    "ups_id": "UPS-001",
                    "timestamp": "2024-03-26T10:30:00",
                    "input_voltage": 230.5,
                    "battery_soc": 95.0,
                    "health_score": 98.0,
                    "status": "normal"
                },
                "health_status": "healthy"
            }
        }


class FleetSummary(BaseModel):
    """Summary statistics for entire UPS fleet."""
    
    total_units: int
    healthy_units: int
    warning_units: int
    critical_units: int
    average_health_score: float
    average_battery_soc: float
    total_load_kw: float
    units_on_battery: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "total_units": 12,
                "healthy_units": 9,
                "warning_units": 2,
                "critical_units": 1,
                "average_health_score": 87.5,
                "average_battery_soc": 92.3,
                "total_load_kw": 85.4,
                "units_on_battery": 0
            }
        }


class TelemetryHistory(BaseModel):
    """Historical telemetry data for a UPS."""
    
    ups_id: str
    start_time: datetime
    end_time: datetime
    data_points: list[UPSTelemetry]
    interval_minutes: int = Field(default=5, description="Interval between data points")
    
    class Config:
        json_schema_extra = {
            "example": {
                "ups_id": "UPS-001",
                "start_time": "2024-03-26T00:00:00",
                "end_time": "2024-03-26T23:59:59",
                "data_points": [],
                "interval_minutes": 5
            }
        }
