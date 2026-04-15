"""
Simulation Models
Pydantic models for strategy settings and what-if scenario simulation.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from enum import Enum


class StrategyMode(str, Enum):
    safety = "safety"
    balanced = "balanced"
    profit = "profit"


class StrategySettings(BaseModel):
    mode: StrategyMode = StrategyMode.balanced
    aggressiveness: int = Field(default=50, ge=0, le=100)  # 0=pure safety, 100=pure profit


class StrategyImpact(BaseModel):
    mode: str
    aggressiveness: int
    projected_revenue_change_pct: float   # % vs baseline (0 = no change)
    battery_degradation_impact_pct: float  # % increased wear vs baseline
    backup_headroom_minutes: float         # estimated backup runtime available
    recommended_min_soc: float             # minimum SOC to maintain
    max_discharge_rate: float              # max % SOC to discharge per hour
    risk_level: str                        # low / medium / high / critical
    recommendations: List[str]


class ScenarioType(str, Enum):
    price_spike = "price_spike"
    load_surge = "load_surge"
    grid_failure = "grid_failure"
    battery_degradation = "battery_degradation"


class SimulationRequest(BaseModel):
    scenario_type: ScenarioType
    ups_ids: List[str] = []   # empty = run on all fleet
    parameters: Dict = {}


class UnitScenarioResult(BaseModel):
    ups_id: str
    current_health: float
    projected_health: float
    current_runtime_minutes: float
    projected_runtime_minutes: float
    current_risk_level: str
    projected_risk_level: str
    current_failure_probability: float
    projected_failure_probability: float
    time_to_critical_minutes: Optional[float] = None
    delta_health: float              # projected - current
    delta_runtime: float             # projected - current
    alerts_triggered: List[str]
    mitigation_actions: List[str]
    severity: str                    # low / medium / high / critical


class SimulationResult(BaseModel):
    scenario_type: str
    scenario_title: str
    scenario_description: str
    fleet_units_affected: int
    fleet_units_going_critical: int
    estimated_first_failure_minutes: Optional[float] = None
    fleet_avg_health_current: float
    fleet_avg_health_projected: float
    fleet_avg_runtime_current: float
    fleet_avg_runtime_projected: float
    unit_results: List[UnitScenarioResult]
    recommendations: List[str]
