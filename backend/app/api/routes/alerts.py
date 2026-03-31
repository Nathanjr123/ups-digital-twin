"""
Alert API Routes
Endpoints for alert management and statistics.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from app.models.alert import Alert, AlertUpdate, AlertStats, AlertList
from app.services.alert_service import AlertService

router = APIRouter(prefix="/alerts", tags=["Alerts"])

# Service instance
alert_service: AlertService = None


def init_alert_routes(service: AlertService):
    """Initialize routes with service instance."""
    global alert_service
    alert_service = service


@router.get("/", response_model=AlertList)
async def get_alerts(
    ups_id: Optional[str] = Query(None, description="Filter by UPS ID"),
    severity: Optional[str] = Query(None, description="Filter by severity"),
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0)
):
    """Get filtered list of alerts."""
    return alert_service.get_all_alerts(
        ups_id=ups_id,
        severity=severity,
        status=status,
        limit=limit,
        offset=offset
    )


@router.get("/statistics", response_model=AlertStats)
async def get_alert_statistics():
    """Get alert statistics and metrics."""
    return alert_service.get_alert_statistics()


@router.get("/{alert_id}", response_model=Alert)
async def get_alert(alert_id: str):
    """Get specific alert by ID."""
    alert = alert_service.get_alert(alert_id)
    
    if not alert:
        raise HTTPException(status_code=404, detail=f"Alert {alert_id} not found")
    
    return alert


@router.patch("/{alert_id}", response_model=Alert)
async def update_alert(alert_id: str, update: AlertUpdate):
    """Update an alert (acknowledge, resolve, etc.)."""
    alert = alert_service.update_alert(alert_id, update)
    
    if not alert:
        raise HTTPException(status_code=404, detail=f"Alert {alert_id} not found")
    
    return alert
