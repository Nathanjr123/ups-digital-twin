"""
Alert Service
Manages alert creation, updates, and retrieval.
"""

from typing import List, Optional, Dict
from datetime import datetime
from collections import defaultdict

from app.models.alert import (
    Alert,
    AlertCreate,
    AlertUpdate,
    AlertStats,
    AlertList
)
from app.models.prediction import CombinedPrediction


class AlertService:
    """Service for managing alerts."""
    
    def __init__(self):
        self.alerts: Dict[str, Alert] = {}
        self.alerts_by_ups: Dict[str, List[str]] = defaultdict(list)
        
    def create_alert(self, alert_data: AlertCreate) -> Alert:
        """Create a new alert."""
        alert = Alert(**alert_data.model_dump())
        
        self.alerts[alert.alert_id] = alert
        self.alerts_by_ups[alert.ups_id].append(alert.alert_id)
        
        return alert
    
    def get_alert(self, alert_id: str) -> Optional[Alert]:
        """Get specific alert by ID."""
        return self.alerts.get(alert_id)
    
    def update_alert(self, alert_id: str, update: AlertUpdate) -> Optional[Alert]:
        """Update an existing alert."""
        alert = self.alerts.get(alert_id)
        
        if not alert:
            return None
        
        # Update fields
        if update.status:
            alert.status = update.status
            
            if update.status == "acknowledged":
                alert.acknowledged_at = datetime.now()
                alert.acknowledged_by = update.acknowledged_by
                
            elif update.status == "resolved":
                alert.resolved_at = datetime.now()
                alert.resolved_by = update.resolved_by
        
        return alert
    
    def get_all_alerts(
        self,
        ups_id: Optional[str] = None,
        severity: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> AlertList:
        """Get filtered list of alerts."""
        filtered_alerts = list(self.alerts.values())
        
        # Apply filters
        if ups_id:
            filtered_alerts = [a for a in filtered_alerts if a.ups_id == ups_id]
        
        if severity:
            filtered_alerts = [a for a in filtered_alerts if a.severity == severity]
        
        if status:
            filtered_alerts = [a for a in filtered_alerts if a.status == status]
        
        # Sort by timestamp (newest first)
        filtered_alerts.sort(key=lambda a: a.timestamp, reverse=True)
        
        # Paginate
        total = len(filtered_alerts)
        paginated = filtered_alerts[offset:offset + limit]
        
        return AlertList(
            alerts=paginated,
            total=total,
            page=(offset // limit) + 1,
            page_size=limit
        )
    
    def get_alerts_by_ups(self, ups_id: str) -> List[Alert]:
        """Get all alerts for a specific UPS."""
        alert_ids = self.alerts_by_ups.get(ups_id, [])
        return [self.alerts[aid] for aid in alert_ids if aid in self.alerts]
    
    def get_alert_statistics(self) -> AlertStats:
        """Get alert statistics."""
        all_alerts = list(self.alerts.values())
        
        total = len(all_alerts)
        active = sum(1 for a in all_alerts if a.status == "active")
        acknowledged = sum(1 for a in all_alerts if a.status == "acknowledged")
        resolved = sum(1 for a in all_alerts if a.status == "resolved")
        
        critical = sum(1 for a in all_alerts if a.severity == "critical")
        high = sum(1 for a in all_alerts if a.severity == "high")
        warning = sum(1 for a in all_alerts if a.severity == "warning")
        info = sum(1 for a in all_alerts if a.severity == "info")
        
        # Count by type
        alerts_by_type = defaultdict(int)
        for alert in all_alerts:
            alerts_by_type[alert.alert_type] += 1
        
        # Count by UPS
        alerts_by_ups = defaultdict(int)
        for alert in all_alerts:
            alerts_by_ups[alert.ups_id] += 1
        
        return AlertStats(
            total_alerts=total,
            active_alerts=active,
            acknowledged_alerts=acknowledged,
            resolved_alerts=resolved,
            critical_alerts=critical,
            high_alerts=high,
            warning_alerts=warning,
            info_alerts=info,
            alerts_by_type=dict(alerts_by_type),
            alerts_by_ups=dict(alerts_by_ups)
        )
    
    def process_prediction(self, prediction: CombinedPrediction):
        """Process prediction and create alerts if necessary."""
        ups_id = prediction.ups_id
        
        # Check for anomaly
        if prediction.anomaly.is_anomaly and prediction.anomaly.severity in ["high", "critical"]:
            self._create_anomaly_alert(prediction)
        
        # Check for failure prediction
        if prediction.failure.will_fail and prediction.failure.risk_level in ["high", "critical"]:
            self._create_failure_alert(prediction)
        
        # Check for specific conditions
        self._check_temperature_alerts(prediction)
        self._check_battery_alerts(prediction)
    
    def _create_anomaly_alert(self, prediction: CombinedPrediction):
        """Create alert for detected anomaly."""
        # Check if similar alert already exists and is active
        existing = self._find_similar_alert(
            prediction.ups_id,
            "anomaly_detected",
            active_only=True
        )
        
        if existing:
            return  # Don't create duplicate
        
        factors = ", ".join([f.feature for f in prediction.anomaly.contributing_factors[:2]])
        
        alert_data = AlertCreate(
            ups_id=prediction.ups_id,
            alert_type="anomaly_detected",
            severity=prediction.anomaly.severity,
            message=f"Anomaly detected in UPS operation",
            details=f"Contributing factors: {factors}",
            recommended_action="Investigate abnormal parameters and verify UPS status"
        )
        
        self.create_alert(alert_data)
    
    def _create_failure_alert(self, prediction: CombinedPrediction):
        """Create alert for failure prediction."""
        existing = self._find_similar_alert(
            prediction.ups_id,
            "failure_predicted",
            active_only=True
        )
        
        if existing:
            return
        
        days = prediction.failure.time_to_failure_days
        probability = prediction.failure.failure_probability * 100
        
        alert_data = AlertCreate(
            ups_id=prediction.ups_id,
            alert_type="failure_predicted",
            severity=prediction.failure.risk_level if prediction.failure.risk_level != "low" else "warning",
            message=f"Failure predicted in {days} days ({probability:.0f}% probability)",
            details=f"Risk level: {prediction.failure.risk_level}",
            recommended_action="Schedule maintenance inspection and prepare replacement parts"
        )
        
        alert = self.create_alert(alert_data)
        alert.related_metrics = {
            "failure_probability": prediction.failure.failure_probability,
            "time_to_failure_days": prediction.failure.time_to_failure_days
        }
    
    def _check_temperature_alerts(self, prediction: CombinedPrediction):
        """Check for temperature-related alerts."""
        # This would check actual telemetry data
        # For now, check if temperature is in risk factors
        for factor in prediction.failure.risk_factors:
            if "temperature" in factor.feature.lower() and factor.status == "high_risk":
                existing = self._find_similar_alert(
                    prediction.ups_id,
                    "high_temperature",
                    active_only=True
                )
                
                if not existing:
                    alert_data = AlertCreate(
                        ups_id=prediction.ups_id,
                        alert_type="high_temperature",
                        severity="warning",
                        message=f"Elevated temperature detected: {factor.feature}",
                        details=f"Current value: {factor.value}",
                        recommended_action="Check cooling system and ambient conditions"
                    )
                    
                    self.create_alert(alert_data)
                break
    
    def _check_battery_alerts(self, prediction: CombinedPrediction):
        """Check for battery-related alerts."""
        for factor in prediction.failure.risk_factors:
            if "battery" in factor.feature.lower() and factor.status == "high_risk":
                existing = self._find_similar_alert(
                    prediction.ups_id,
                    "low_battery",
                    active_only=True
                )
                
                if not existing:
                    alert_data = AlertCreate(
                        ups_id=prediction.ups_id,
                        alert_type="low_battery",
                        severity="high",
                        message=f"Battery health degraded: {factor.feature}",
                        details=f"Current value: {factor.value}",
                        recommended_action="Test battery capacity and plan replacement"
                    )
                    
                    self.create_alert(alert_data)
                break
    
    def _find_similar_alert(
        self,
        ups_id: str,
        alert_type: str,
        active_only: bool = False
    ) -> Optional[Alert]:
        """Find similar alert to avoid duplicates."""
        ups_alerts = self.get_alerts_by_ups(ups_id)
        
        for alert in ups_alerts:
            if alert.alert_type == alert_type:
                if not active_only or alert.status == "active":
                    return alert
        
        return None
