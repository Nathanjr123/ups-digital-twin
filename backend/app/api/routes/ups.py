"""
UPS API Routes
Endpoints for UPS fleet management and telemetry.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional

from app.models.ups import UPSInfo, UPSTelemetry, FleetSummary, TelemetryHistory
from app.services.ups_service import UPSService

router = APIRouter(prefix="/ups", tags=["UPS"])

# Service instance will be injected via dependency
ups_service = UPSService()


@router.get("/", response_model=List[UPSInfo])
async def get_all_ups():
    """Get information for all UPS units in the fleet."""
    return ups_service.get_all_ups()


@router.get("/fleet-summary", response_model=FleetSummary)
async def get_fleet_summary():
    """Get fleet-wide summary statistics."""
    return ups_service.get_fleet_summary()


@router.get("/{ups_id}", response_model=UPSInfo)
async def get_ups(ups_id: str):
    """Get detailed information for a specific UPS."""
    ups = ups_service.get_ups_by_id(ups_id)
    
    if not ups:
        raise HTTPException(status_code=404, detail=f"UPS {ups_id} not found")
    
    return ups


@router.get("/{ups_id}/telemetry", response_model=UPSTelemetry)
async def get_ups_telemetry(ups_id: str):
    """Get latest telemetry data for a specific UPS."""
    telemetry = ups_service.get_latest_telemetry(ups_id)
    
    if not telemetry:
        raise HTTPException(status_code=404, detail=f"UPS {ups_id} not found")
    
    return telemetry


@router.get("/{ups_id}/history", response_model=TelemetryHistory)
async def get_ups_history(
    ups_id: str,
    hours: int = Query(24, ge=1, le=168, description="Hours of history to retrieve")
):
    """Get historical telemetry data for a specific UPS."""
    history = ups_service.get_telemetry_history(ups_id, hours)
    
    if not history:
        raise HTTPException(
            status_code=404,
            detail=f"No history available for UPS {ups_id}"
        )
    
    return history
