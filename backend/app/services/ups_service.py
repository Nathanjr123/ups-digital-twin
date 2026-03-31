"""
UPS Service
Business logic for UPS operations and data management.
"""

from typing import List, Dict, Optional
from datetime import datetime, timedelta
from collections import defaultdict

from app.ml.data_generator import FleetDataGenerator, UPSDataGenerator
from app.models.ups import (
    UPSTelemetry,
    UPSMetadata,
    UPSInfo,
    FleetSummary,
    TelemetryHistory
)


class UPSService:
    """Service for managing UPS fleet operations."""
    
    def __init__(self):
        self.fleet_generator = FleetDataGenerator()
        self.telemetry_cache: Dict[str, List[Dict]] = defaultdict(list)
        self.max_cache_size = 288  # 24 hours at 5-minute intervals
        
    def _clamp_telemetry(self, data: Dict) -> Dict:
        """Clamp telemetry values to valid Pydantic ranges."""
        data["input_voltage"] = max(0, min(500, data.get("input_voltage", 230)))
        data["input_current"] = max(0, data.get("input_current", 0))
        data["input_frequency"] = max(45, min(65, data.get("input_frequency", 50)))
        data["output_voltage"] = max(0, min(500, data.get("output_voltage", 230)))
        data["output_current"] = max(0, data.get("output_current", 0))
        data["output_frequency"] = max(45, min(65, data.get("output_frequency", 50)))
        data["battery_voltage"] = max(0, data.get("battery_voltage", 52))
        data["battery_soc"] = max(0, min(100, data.get("battery_soc", 100)))
        data["runtime_remaining"] = max(0, data.get("runtime_remaining", 0))
        data["load_percentage"] = max(0, min(100, data.get("load_percentage", 0)))
        data["health_score"] = max(0, min(100, data.get("health_score", 100)))
        return data

    def get_all_ups(self) -> List[UPSInfo]:
        """Get information for all UPS units."""
        ups_list = []

        for ups in self.fleet_generator.fleet:
            data = self._clamp_telemetry(ups.generate_data_point())

            metadata = UPSMetadata(
                ups_id=ups.ups_id,
                location=ups.location,
                model=ups.model,
                installation_date=ups.installation_date,
                last_maintenance=ups.last_maintenance
            )

            telemetry = UPSTelemetry(**data)
            
            health_status = self._determine_health_status(data)
            
            ups_info = UPSInfo(
                metadata=metadata,
                latest_telemetry=telemetry,
                health_status=health_status
            )
            
            ups_list.append(ups_info)
        
        return ups_list
    
    def get_ups_by_id(self, ups_id: str) -> Optional[UPSInfo]:
        """Get information for specific UPS."""
        try:
            ups = self.fleet_generator.get_ups_by_id(ups_id)
            data = self._clamp_telemetry(ups.generate_data_point())

            metadata = UPSMetadata(
                ups_id=ups.ups_id,
                location=ups.location,
                model=ups.model,
                installation_date=ups.installation_date,
                last_maintenance=ups.last_maintenance
            )

            telemetry = UPSTelemetry(**data)
            health_status = self._determine_health_status(data)

            return UPSInfo(
                metadata=metadata,
                latest_telemetry=telemetry,
                health_status=health_status
            )
        except ValueError:
            return None
    
    def get_latest_telemetry(self, ups_id: str) -> Optional[UPSTelemetry]:
        """Get latest telemetry for specific UPS."""
        try:
            ups = self.fleet_generator.get_ups_by_id(ups_id)
            data = self._clamp_telemetry(ups.generate_data_point())

            # Cache the data
            self._cache_telemetry(ups_id, data)

            return UPSTelemetry(**data)
        except ValueError:
            return None
    
    def get_telemetry_history(
        self,
        ups_id: str,
        hours: int = 24
    ) -> Optional[TelemetryHistory]:
        """Get historical telemetry for specific UPS."""
        # Check cache first
        cached_data = self.telemetry_cache.get(ups_id, [])
        
        if not cached_data:
            # Generate historical data if cache is empty
            cached_data = self._generate_historical_telemetry(ups_id, hours)
        
        # Filter by time range
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=hours)
        
        filtered_data = [
            d for d in cached_data
            if start_time <= datetime.fromisoformat(d["timestamp"]) <= end_time
        ]
        
        if not filtered_data:
            return None
        
        telemetry_list = [UPSTelemetry(**d) for d in filtered_data]
        
        return TelemetryHistory(
            ups_id=ups_id,
            start_time=start_time,
            end_time=end_time,
            data_points=telemetry_list,
            interval_minutes=5
        )
    
    def get_fleet_summary(self) -> FleetSummary:
        """Get fleet-wide statistics."""
        all_ups = self.get_all_ups()
        
        total = len(all_ups)
        healthy = sum(1 for u in all_ups if u.health_status == "healthy")
        warning = sum(1 for u in all_ups if u.health_status == "warning")
        critical = sum(1 for u in all_ups if u.health_status == "critical")
        
        health_scores = [u.latest_telemetry.health_score for u in all_ups]
        battery_socs = [u.latest_telemetry.battery_soc for u in all_ups]
        loads = [u.latest_telemetry.load_percentage for u in all_ups]
        on_battery = sum(1 for u in all_ups if u.latest_telemetry.on_battery)
        
        avg_health = sum(health_scores) / len(health_scores) if health_scores else 0
        avg_soc = sum(battery_socs) / len(battery_socs) if battery_socs else 0
        total_load = sum(loads) * 0.1  # Rough estimate in kW
        
        return FleetSummary(
            total_units=total,
            healthy_units=healthy,
            warning_units=warning,
            critical_units=critical,
            average_health_score=round(avg_health, 2),
            average_battery_soc=round(avg_soc, 2),
            total_load_kw=round(total_load, 2),
            units_on_battery=on_battery
        )
    
    def generate_fleet_snapshot(self) -> List[UPSTelemetry]:
        """Generate current telemetry snapshot for entire fleet."""
        snapshot = self.fleet_generator.generate_fleet_snapshot()

        result = []
        for data in snapshot:
            data = self._clamp_telemetry(data)
            self._cache_telemetry(data["ups_id"], data)
            result.append(UPSTelemetry(**data))

        return result
    
    def _determine_health_status(self, data: Dict) -> str:
        """Determine health status from telemetry."""
        status = data.get("status", "normal")
        health_score = data.get("health_score", 100)
        
        if status in ["critical", "failure"] or health_score < 60:
            return "critical"
        elif status == "warning" or health_score < 80:
            return "warning"
        else:
            return "healthy"
    
    def _cache_telemetry(self, ups_id: str, data: Dict):
        """Cache telemetry data for historical queries."""
        cache = self.telemetry_cache[ups_id]
        cache.append(data)
        
        # Trim cache if too large
        if len(cache) > self.max_cache_size:
            cache.pop(0)
    
    def _generate_historical_telemetry(self, ups_id: str, hours: int) -> List[Dict]:
        """Generate historical telemetry data for caching."""
        try:
            ups = self.fleet_generator.get_ups_by_id(ups_id)
            historical_data = []
            
            # Generate data at 5-minute intervals
            num_points = (hours * 60) // 5
            
            for i in range(num_points):
                timestamp = datetime.now() - timedelta(minutes=(num_points - i) * 5)
                data = ups.generate_data_point()
                data["timestamp"] = timestamp.isoformat()
                historical_data.append(data)
            
            # Cache it
            self.telemetry_cache[ups_id] = historical_data
            
            return historical_data
        except ValueError:
            return []
