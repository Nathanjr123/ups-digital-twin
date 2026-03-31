"""
Synthetic UPS Data Generator
Generates realistic UPS sensor data with various operational patterns and failure scenarios.
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Literal
import random


class UPSDataGenerator:
    """Generate synthetic UPS telemetry data with realistic patterns."""
    
    def __init__(self, ups_id: str, location: str, model: str):
        self.ups_id = ups_id
        self.location = location
        self.model = model
        self.installation_date = datetime.now() - timedelta(days=random.randint(365, 1825))
        self.last_maintenance = datetime.now() - timedelta(days=random.randint(30, 180))
        
        # Operating state
        self.battery_capacity_degradation = random.uniform(0.85, 1.0)  # 85-100% of original
        self.health_score = random.uniform(70, 100)
        self.failure_mode: Literal["none", "battery_degradation", "overload", "cooling_failure", "input_power"] = "none"
        self.failure_day = 0
        
    def generate_normal_operation(self) -> Dict:
        """Generate data for normal UPS operation."""
        load_pct = random.uniform(30, 75)  # Normal load range
        
        return {
            "ups_id": self.ups_id,
            "timestamp": datetime.now().isoformat(),
            "location": self.location,
            "model": self.model,
            
            # Input power
            "input_voltage": random.gauss(230, 2),  # Stable input
            "input_current": load_pct * 0.5 + random.gauss(0, 1),
            "input_frequency": random.gauss(50, 0.1),
            
            # Output power
            "output_voltage": random.gauss(230, 0.5),  # Very stable output
            "output_current": load_pct * 0.5 + random.gauss(0, 0.5),
            "output_frequency": 50.0,
            
            # Battery
            "battery_voltage": random.gauss(52, 0.5) * self.battery_capacity_degradation,
            "battery_current": random.gauss(-2, 0.5),  # Slight charging
            "battery_soc": random.uniform(95, 100) * self.battery_capacity_degradation,
            "battery_temperature": random.gauss(25, 2),
            "runtime_remaining": max(0, int((100 * self.battery_capacity_degradation - load_pct) * 1.5)),
            
            # System
            "load_percentage": load_pct,
            "inverter_temperature": random.gauss(40, 3),
            "ambient_temperature": random.gauss(23, 2),
            
            # Status
            "health_score": self.health_score,
            "status": "normal",
            "on_battery": False,
            "last_maintenance": self.last_maintenance.isoformat(),
        }
    
    def generate_battery_degradation(self, day: int) -> Dict:
        """Simulate progressive battery degradation over 14 days."""
        base_data = self.generate_normal_operation()
        
        # Progressive degradation
        degradation_factor = 1.0 - (day / 14) * 0.4  # Lose 40% capacity over 14 days
        self.battery_capacity_degradation = degradation_factor
        
        base_data["battery_voltage"] = random.gauss(52, 1) * degradation_factor - (day * 0.3)
        base_data["battery_soc"] = random.uniform(60, 90) * degradation_factor
        base_data["battery_temperature"] = random.gauss(25, 2) + (day * 1.5)  # Rising temp
        base_data["runtime_remaining"] = max(0, int(base_data["runtime_remaining"] * degradation_factor))
        base_data["health_score"] = 100 * degradation_factor
        
        if day > 10:
            base_data["status"] = "warning"
        if day > 12:
            base_data["status"] = "critical"
            
        return base_data
    
    def generate_overload_condition(self) -> Dict:
        """Simulate UPS under overload stress."""
        base_data = self.generate_normal_operation()
        
        load_pct = random.uniform(85, 100)  # High load
        
        base_data["load_percentage"] = load_pct
        base_data["output_current"] = load_pct * 0.6 + random.gauss(0, 2)
        base_data["inverter_temperature"] = random.gauss(60, 5)  # High temp
        base_data["battery_temperature"] = random.gauss(35, 3)  # Elevated
        base_data["battery_soc"] = random.uniform(70, 85)  # Discharging faster
        base_data["runtime_remaining"] = max(0, int(base_data["runtime_remaining"] * 0.6))
        base_data["health_score"] = random.uniform(60, 75)
        base_data["status"] = "warning"
        
        return base_data
    
    def generate_cooling_failure(self, hours_since_failure: int) -> Dict:
        """Simulate cooling system failure with progressive temperature rise."""
        base_data = self.generate_normal_operation()

        # Temperature rises over time, capped at realistic maximums
        hours_capped = min(hours_since_failure, 12)
        temp_increase = hours_capped * 3

        base_data["inverter_temperature"] = min(85, random.gauss(40, 3) + temp_increase)
        base_data["battery_temperature"] = min(65, random.gauss(25, 2) + temp_increase * 0.7)
        base_data["ambient_temperature"] = min(45, random.gauss(23, 2) + temp_increase * 0.5)

        base_data["health_score"] = max(30, 100 - temp_increase * 5)

        if hours_since_failure > 3:
            base_data["status"] = "warning"
        if hours_since_failure > 6:
            base_data["status"] = "critical"

        return base_data
    
    def generate_input_power_instability(self) -> Dict:
        """Simulate unstable input power with voltage fluctuations."""
        base_data = self.generate_normal_operation()
        
        # Voltage swings
        base_data["input_voltage"] = random.gauss(230, 15)  # High variance
        base_data["input_frequency"] = random.gauss(50, 0.5)  # Unstable frequency
        
        # UPS compensating
        base_data["battery_current"] = random.gauss(5, 3)  # Discharging to compensate
        base_data["battery_soc"] = random.uniform(70, 90)
        base_data["on_battery"] = random.choice([True, False])
        
        base_data["health_score"] = random.uniform(65, 80)
        base_data["status"] = "warning"
        
        return base_data
    
    def generate_anomaly(self) -> Dict:
        """Generate data with random anomaly."""
        base_data = self.generate_normal_operation()
        
        anomaly_type = random.choice([
            "voltage_spike",
            "temp_spike",
            "load_spike",
            "battery_anomaly"
        ])
        
        if anomaly_type == "voltage_spike":
            base_data["input_voltage"] = random.choice([random.uniform(190, 210), random.uniform(250, 270)])
            base_data["output_voltage"] = random.gauss(230, 3)
            
        elif anomaly_type == "temp_spike":
            base_data["inverter_temperature"] = random.uniform(55, 70)
            base_data["battery_temperature"] = random.uniform(35, 45)
            
        elif anomaly_type == "load_spike":
            base_data["load_percentage"] = random.uniform(80, 95)
            base_data["output_current"] = base_data["load_percentage"] * 0.6
            
        elif anomaly_type == "battery_anomaly":
            base_data["battery_voltage"] = random.uniform(45, 48)
            base_data["battery_soc"] = random.uniform(50, 70)
            
        base_data["status"] = "anomaly_detected"
        
        return base_data
    
    def set_failure_mode(self, mode: Literal["none", "battery_degradation", "overload", "cooling_failure", "input_power"]):
        """Set the failure mode for this UPS."""
        self.failure_mode = mode
        self.failure_day = 0
    
    def generate_data_point(self) -> Dict:
        """Generate a single data point based on current failure mode."""
        if self.failure_mode == "battery_degradation":
            self.failure_day = min(self.failure_day + 0.1, 14)
            return self.generate_battery_degradation(int(self.failure_day))

        elif self.failure_mode == "overload":
            return self.generate_overload_condition()

        elif self.failure_mode == "cooling_failure":
            self.failure_day = min(self.failure_day + 0.1, 1)  # Cap at ~24 hours
            return self.generate_cooling_failure(int(self.failure_day * 24))
        
        elif self.failure_mode == "input_power":
            return self.generate_input_power_instability()
        
        else:
            # 5% chance of random anomaly in normal operation
            if random.random() < 0.05:
                return self.generate_anomaly()
            return self.generate_normal_operation()


class FleetDataGenerator:
    """Manage data generation for entire UPS fleet."""
    
    def __init__(self):
        self.fleet = self._initialize_fleet()
        
    def _initialize_fleet(self) -> List[UPSDataGenerator]:
        """Create fleet of 12 UPS units."""
        locations = [
            "Building A - Server Room",
            "Building A - Data Center",
            "Building B - Control Room",
            "Building C - Manufacturing",
            "Mine Shaft 3 - Control",
            "Mine Shaft 3 - Pumps",
            "Mine Shaft 5 - Ventilation",
            "Production Line 1",
            "Production Line 2",
            "Warehouse - Cold Storage",
            "Admin Building",
            "Emergency Systems"
        ]
        
        models = [
            "PowerGuard 10kVA",
            "PowerGuard 15kVA",
            "IndustrialPro 20kVA",
            "IndustrialPro 30kVA",
            "MegaWatt 50kVA"
        ]
        
        fleet = []
        for i in range(12):
            ups_id = f"UPS-{str(i+1).zfill(3)}"
            ups = UPSDataGenerator(
                ups_id=ups_id,
                location=locations[i],
                model=random.choice(models)
            )
            fleet.append(ups)
        
        # Set some units to failure modes for demo
        fleet[8].set_failure_mode("battery_degradation")  # UPS-009
        fleet[10].set_failure_mode("overload")  # UPS-011
        fleet[11].set_failure_mode("cooling_failure")  # UPS-012
        
        return fleet
    
    def generate_fleet_snapshot(self) -> List[Dict]:
        """Generate current data for entire fleet."""
        return [ups.generate_data_point() for ups in self.fleet]
    
    def get_ups_by_id(self, ups_id: str) -> UPSDataGenerator:
        """Get specific UPS generator."""
        for ups in self.fleet:
            if ups.ups_id == ups_id:
                return ups
        raise ValueError(f"UPS {ups_id} not found")
    
    def generate_historical_data(self, days: int = 30) -> pd.DataFrame:
        """Generate historical data for training ML models."""
        records = []
        
        for day in range(days * 24):  # Hourly data
            timestamp = datetime.now() - timedelta(hours=days * 24 - day)
            
            for ups in self.fleet:
                data = ups.generate_data_point()
                data["timestamp"] = timestamp.isoformat()
                records.append(data)
        
        return pd.DataFrame(records)
