"""
Simulation Service
Handles strategy mode logic and what-if scenario simulation.
"""

import copy
import logging
from typing import Dict, List, Optional

from app.models.simulation import (
    StrategyMode, StrategySettings, StrategyImpact,
    ScenarioType, SimulationRequest, SimulationResult, UnitScenarioResult,
)

logger = logging.getLogger(__name__)

# Risk-level thresholds for failure probability
def _risk_from_prob(p: float) -> str:
    if p < 0.20:
        return "low"
    if p < 0.45:
        return "medium"
    if p < 0.70:
        return "high"
    return "critical"


def _severity_from_delta(delta_health: float, projected_risk: str) -> str:
    if projected_risk == "critical" or delta_health < -20:
        return "critical"
    if projected_risk == "high" or delta_health < -10:
        return "high"
    if projected_risk == "medium" or delta_health < -5:
        return "medium"
    return "low"


class SimulationService:
    """Core service for strategy impact and what-if scenario simulation."""

    def __init__(self, ups_service, prediction_service):
        self.ups_service = ups_service
        self.prediction_service = prediction_service
        self._strategy = StrategySettings()

    # ------------------------------------------------------------------ #
    #  Strategy                                                            #
    # ------------------------------------------------------------------ #

    def get_strategy(self) -> StrategySettings:
        return self._strategy

    def set_strategy(self, settings: StrategySettings) -> StrategyImpact:
        self._strategy = settings
        return self.compute_strategy_impact(settings)

    def compute_strategy_impact(self, settings: StrategySettings) -> StrategyImpact:
        agg = settings.aggressiveness  # 0-100

        # Revenue gain from energy arbitrage (discharge at peak prices)
        #   0  → 0 % extra revenue (no arbitrage)
        #  50  → +15 %
        # 100  → +30 %
        revenue_change = round(agg * 0.30, 1)

        # Battery degradation from extra cycling
        #   0  → 0 %
        #  50  → +17 %
        # 100  → +35 %
        degradation_impact = round(agg * 0.35, 1)

        # Minimum SOC we must keep (safety headroom)
        # safety=0 → 80 %, profit=100 → 20 %
        min_soc = max(20.0, 80.0 - agg * 0.60)

        # Rough backup headroom: assume 1.2 min per % SOC above 0 at average load
        backup_headroom = round(min_soc * 1.5, 0)

        # Max discharge rate per hour
        max_discharge_rate = round(5.0 + agg * 0.15, 1)

        if agg < 25:
            risk_level = "low"
            recs = [
                "Conservative operation — backup readiness is maximised.",
                "Maintain battery SOC above 80 % at all times.",
                "Avoid energy arbitrage cycles to extend battery life.",
                "Schedule maintenance during low-load windows.",
            ]
        elif agg < 50:
            risk_level = "low"
            recs = [
                "Balanced operation with modest revenue optimisation.",
                "Allow discharge to 50 % SOC during peak price windows.",
                "Monitor battery temperature during discharge cycles.",
                "Recharge to 80 %+ before expected peak-load periods.",
            ]
        elif agg < 75:
            risk_level = "medium"
            recs = [
                "Revenue-optimised mode — battery wear is elevated.",
                "Set discharge floor at 35 % SOC to retain backup capacity.",
                "Increase battery health monitoring frequency.",
                "Ensure cooling systems are fully operational.",
            ]
        else:
            risk_level = "high"
            recs = [
                "Aggressive profit mode — closely monitor battery health.",
                "Keep a 20 % emergency reserve at all times.",
                "Expect accelerated battery replacement intervals.",
                "Do NOT use this mode if grid reliability is below 99 %.",
            ]

        return StrategyImpact(
            mode=settings.mode.value,
            aggressiveness=agg,
            projected_revenue_change_pct=revenue_change,
            battery_degradation_impact_pct=degradation_impact,
            backup_headroom_minutes=backup_headroom,
            recommended_min_soc=round(min_soc, 0),
            max_discharge_rate=max_discharge_rate,
            risk_level=risk_level,
            recommendations=recs,
        )

    # ------------------------------------------------------------------ #
    #  What-If Scenarios                                                   #
    # ------------------------------------------------------------------ #

    def run_scenario(self, request: SimulationRequest) -> SimulationResult:
        """Run a what-if scenario and return projected fleet impact."""

        # Gather current telemetry for selected (or all) units
        all_telemetry = self.ups_service.get_all_ups()
        if request.ups_ids:
            targets = [t for t in all_telemetry if t.latest_telemetry and
                       t.latest_telemetry.ups_id in request.ups_ids]
        else:
            targets = [t for t in all_telemetry if t.latest_telemetry]

        unit_results: List[UnitScenarioResult] = []

        for ups_info in targets:
            tel = ups_info.latest_telemetry
            if tel is None:
                continue

            # Get current predictions
            try:
                current_pred = self.prediction_service.predict_combined(
                    tel.dict() if hasattr(tel, 'dict') else tel.model_dump()
                )
                current_fail_prob = current_pred.failure.failure_probability
                current_risk = current_pred.failure.risk_level
            except Exception:
                current_fail_prob = 0.1
                current_risk = "low"

            # Build a mutated copy for the scenario
            tel_dict = tel.model_dump() if hasattr(tel, 'model_dump') else tel.dict()
            proj_dict = copy.deepcopy(tel_dict)

            scenario_fn = {
                ScenarioType.price_spike: self._scenario_price_spike,
                ScenarioType.load_surge: self._scenario_load_surge,
                ScenarioType.grid_failure: self._scenario_grid_failure,
                ScenarioType.battery_degradation: self._scenario_battery_degradation,
            }[request.scenario_type]

            proj_dict, alerts, mitigations, time_to_critical = scenario_fn(
                proj_dict, request.parameters
            )

            # Re-run predictions on projected telemetry
            try:
                proj_pred = self.prediction_service.predict_combined(proj_dict)
                proj_fail_prob = proj_pred.failure.failure_probability
                proj_risk = proj_pred.failure.risk_level
            except Exception:
                proj_fail_prob = min(1.0, current_fail_prob + 0.30)
                proj_risk = _risk_from_prob(proj_fail_prob)

            proj_health = float(proj_dict.get("health_score", tel_dict.get("health_score", 50)))
            curr_health = float(tel_dict.get("health_score", 50))
            proj_runtime = float(proj_dict.get("runtime_remaining", 0))
            curr_runtime = float(tel_dict.get("runtime_remaining", 0))

            delta_health = proj_health - curr_health
            delta_runtime = proj_runtime - curr_runtime

            unit_results.append(UnitScenarioResult(
                ups_id=tel.ups_id,
                current_health=round(curr_health, 1),
                projected_health=round(proj_health, 1),
                current_runtime_minutes=round(curr_runtime, 0),
                projected_runtime_minutes=round(proj_runtime, 0),
                current_risk_level=current_risk,
                projected_risk_level=proj_risk,
                current_failure_probability=round(current_fail_prob, 3),
                projected_failure_probability=round(proj_fail_prob, 3),
                time_to_critical_minutes=time_to_critical,
                delta_health=round(delta_health, 1),
                delta_runtime=round(delta_runtime, 0),
                alerts_triggered=alerts,
                mitigation_actions=mitigations,
                severity=_severity_from_delta(delta_health, proj_risk),
            ))

        # Aggregate stats
        going_critical = sum(1 for r in unit_results if r.projected_risk_level == "critical")
        affected = sum(1 for r in unit_results if r.delta_health < -2 or r.delta_runtime < -5)
        first_fail = min(
            (r.time_to_critical_minutes for r in unit_results if r.time_to_critical_minutes is not None),
            default=None,
        )
        avg_health_now = (sum(r.current_health for r in unit_results) / len(unit_results)
                          if unit_results else 0)
        avg_health_proj = (sum(r.projected_health for r in unit_results) / len(unit_results)
                           if unit_results else 0)
        avg_runtime_now = (sum(r.current_runtime_minutes for r in unit_results) / len(unit_results)
                           if unit_results else 0)
        avg_runtime_proj = (sum(r.projected_runtime_minutes for r in unit_results) / len(unit_results)
                            if unit_results else 0)

        meta = self._scenario_meta(request.scenario_type, going_critical)

        return SimulationResult(
            scenario_type=request.scenario_type.value,
            scenario_title=meta["title"],
            scenario_description=meta["description"],
            fleet_units_affected=affected,
            fleet_units_going_critical=going_critical,
            estimated_first_failure_minutes=first_fail,
            fleet_avg_health_current=round(avg_health_now, 1),
            fleet_avg_health_projected=round(avg_health_proj, 1),
            fleet_avg_runtime_current=round(avg_runtime_now, 0),
            fleet_avg_runtime_projected=round(avg_runtime_proj, 0),
            unit_results=sorted(unit_results, key=lambda r: r.delta_health),
            recommendations=meta["recommendations"],
        )

    # ------------------------------------------------------------------ #
    #  Individual scenario mutators                                        #
    # ------------------------------------------------------------------ #

    def _scenario_price_spike(self, tel: dict, params: dict):
        """Energy prices spike 3× — profit mode discharges aggressively."""
        multiplier = params.get("price_multiplier", 3.0)
        agg = self._strategy.aggressiveness

        # Higher aggressiveness → deeper discharge during spike
        discharge_depth = agg * 0.30  # up to 30 % SOC reduction
        tel["battery_soc"] = max(15.0, tel.get("battery_soc", 80) - discharge_depth)
        tel["runtime_remaining"] = max(5.0, tel.get("runtime_remaining", 60) * (tel["battery_soc"] / max(1, tel.get("battery_soc", 80) + discharge_depth)))
        tel["battery_temperature"] = min(65.0, tel.get("battery_temperature", 25) + discharge_depth * 0.3)
        tel["health_score"] = max(0.0, tel.get("health_score", 100) - discharge_depth * 0.2)

        alerts = []
        mitigations = []
        time_to_critical = None

        if tel["battery_soc"] < 40:
            alerts.append(f"Battery SOC critically low at {tel['battery_soc']:.0f}% during price spike discharge")
            mitigations.append("Set minimum SOC floor at 30 % to retain backup capacity")
            time_to_critical = tel["runtime_remaining"] * 0.5

        if agg > 70:
            alerts.append("Aggressive discharge may compromise backup protection during spike window")
            mitigations.append("Limit price-spike discharge to off-peak hours only")

        mitigations.append(f"Revenue opportunity: +{(multiplier - 1) * 15 * (agg / 100):.0f}% from arbitrage")
        return tel, alerts, mitigations, time_to_critical

    def _scenario_load_surge(self, tel: dict, params: dict):
        """Critical load doubles in 10 minutes."""
        surge_factor = params.get("surge_factor", 2.0)
        current_load = tel.get("load_percentage", 50)
        new_load = min(100.0, current_load * surge_factor)

        tel["load_percentage"] = new_load
        # More load → faster discharge → less runtime
        tel["runtime_remaining"] = max(1.0, tel.get("runtime_remaining", 60) / surge_factor)
        # Higher load → more heat
        tel["inverter_temperature"] = min(90.0, tel.get("inverter_temperature", 40) + (new_load - current_load) * 0.4)
        tel["battery_temperature"] = min(65.0, tel.get("battery_temperature", 25) + (new_load - current_load) * 0.2)
        tel["output_current"] = tel.get("output_current", 10) * surge_factor
        # Health degrades under sustained overload
        tel["health_score"] = max(0.0, tel.get("health_score", 100) - max(0, new_load - 85) * 0.5)

        alerts = []
        mitigations = []
        time_to_critical = None

        if new_load > 95:
            alerts.append(f"Overload condition: {new_load:.0f}% load exceeds rated capacity")
            time_to_critical = tel["runtime_remaining"]
            mitigations.append("Activate load-shedding on non-critical circuits immediately")
        elif new_load > 85:
            alerts.append(f"High load warning: {new_load:.0f}% — approaching rated capacity")
            mitigations.append("Prepare load-shedding plan for non-essential equipment")

        if tel["inverter_temperature"] > 70:
            alerts.append(f"Inverter overheating at {tel['inverter_temperature']:.0f}°C under surge load")
            mitigations.append("Verify cooling systems are running at full capacity")

        mitigations.append("Identify and prioritise critical vs non-critical loads")
        return tel, alerts, mitigations, time_to_critical

    def _scenario_grid_failure(self, tel: dict, params: dict):
        """Grid fails — UPS switches to battery, simulate until exhaustion."""
        # All units switch to battery immediately
        tel["on_battery"] = True
        current_soc = tel.get("battery_soc", 80)
        load = tel.get("load_percentage", 50)

        # Discharge rate increases with load
        discharge_rate_per_min = (load / 100) * 0.5  # % SOC per minute
        runtime_to_empty = current_soc / discharge_rate_per_min if discharge_rate_per_min > 0 else 999

        tel["runtime_remaining"] = max(1.0, runtime_to_empty)
        # Running on battery raises temps slightly
        tel["battery_temperature"] = min(65.0, tel.get("battery_temperature", 25) + 3.0)
        tel["inverter_temperature"] = min(85.0, tel.get("inverter_temperature", 40) + 5.0)

        # SOC drains proportionally to load during failure window
        failure_duration = params.get("failure_duration_minutes", 30)
        soc_after = max(0.0, current_soc - discharge_rate_per_min * failure_duration)
        tel["battery_soc"] = soc_after
        tel["health_score"] = max(0.0, tel.get("health_score", 100) - max(0, (50 - soc_after) * 0.3))

        alerts = []
        mitigations = []

        alerts.append(f"Grid failure — unit operating on battery. Runtime: {runtime_to_empty:.0f} min")
        time_to_critical = runtime_to_empty if runtime_to_empty < 60 else None

        if runtime_to_empty < 15:
            alerts.append(f"CRITICAL: Battery will be exhausted in {runtime_to_empty:.0f} minutes")
            mitigations.append("Initiate emergency shutdown of non-essential equipment NOW")
        elif runtime_to_empty < 30:
            alerts.append(f"WARNING: Less than 30 minutes backup remaining")
            mitigations.append("Begin controlled shutdown of non-critical systems")

        mitigations.append("Dispatch maintenance team to restore grid power")
        mitigations.append("Activate backup generator if available")
        return tel, alerts, mitigations, time_to_critical

    def _scenario_battery_degradation(self, tel: dict, params: dict):
        """Battery State-of-Health drops to 85 % — capacity reduced."""
        target_soh = params.get("target_soh_pct", 85) / 100  # e.g. 0.85

        capacity_ratio = target_soh  # effective capacity fraction
        tel["battery_soc"] = tel.get("battery_soc", 80) * capacity_ratio
        tel["runtime_remaining"] = max(1.0, tel.get("runtime_remaining", 60) * capacity_ratio)
        tel["battery_voltage"] = max(44.0, tel.get("battery_voltage", 52) * capacity_ratio)
        # Degraded batteries run hotter
        tel["battery_temperature"] = min(65.0, tel.get("battery_temperature", 25) + (1 - capacity_ratio) * 30)
        tel["health_score"] = max(0.0, tel.get("health_score", 100) * capacity_ratio)

        alerts = []
        mitigations = []
        time_to_critical = None

        soh_drop = (1 - target_soh) * 100
        alerts.append(f"Battery SoH degraded to {target_soh * 100:.0f}% — effective capacity reduced by {soh_drop:.0f}%")

        if tel["battery_soc"] < 50:
            alerts.append(f"Effective SOC after degradation: {tel['battery_soc']:.0f}% — backup protection compromised")
            time_to_critical = tel["runtime_remaining"]
            mitigations.append("Schedule battery replacement within 30 days")
        else:
            mitigations.append("Plan battery replacement within 90 days")

        if tel["battery_temperature"] > 35:
            alerts.append(f"Elevated battery temperature {tel['battery_temperature']:.0f}°C accelerating further degradation")
            mitigations.append("Improve battery compartment cooling")

        mitigations.append("Run full battery capacity test to confirm SoH reading")
        return tel, alerts, mitigations, time_to_critical

    # ------------------------------------------------------------------ #
    #  Scenario metadata                                                   #
    # ------------------------------------------------------------------ #

    def _scenario_meta(self, scenario_type: ScenarioType, going_critical: int) -> dict:
        meta = {
            ScenarioType.price_spike: {
                "title": "Energy Price Spike 3×",
                "description": "Energy prices surge to 3× current rate. Profit mode discharges batteries aggressively to capitalise on arbitrage. Simulates battery SOC reduction, runtime impact, and thermal stress.",
                "recommendations": [
                    "Pre-charge batteries to 100% before forecast price windows.",
                    "Set a hard SOC floor (≥ 30%) to preserve backup capability.",
                    "Only activate deep discharge on units with healthy batteries (SoH > 90%).",
                    "Monitor battery temperature closely during discharge cycles.",
                ],
            },
            ScenarioType.load_surge: {
                "title": "Critical Load Surge 2×",
                "description": "Connected load doubles within 10 minutes due to equipment startup or demand spike. Simulates overload conditions, thermal rise, and accelerated battery discharge.",
                "recommendations": [
                    "Implement automatic load-shedding at 90% capacity.",
                    "Distribute load across multiple UPS units to avoid single-point overload.",
                    "Verify cooling systems can handle sustained high-load operation.",
                    "Identify non-critical loads that can be dropped instantly.",
                ],
            },
            ScenarioType.grid_failure: {
                "title": "Grid Failure at 2 PM",
                "description": "Complete grid outage at peak load time. All UPS units switch to battery. Simulates runtime to exhaustion based on current SOC and load profile.",
                "recommendations": [
                    "Ensure all units have ≥ 80% SOC before typical high-risk windows.",
                    "Install or test backup generators for extended outages.",
                    "Prioritise critical loads — identify systems that can survive on partial backup.",
                    f"{'CRITICAL: ' + str(going_critical) + ' units will exhaust batteries within 30 minutes.' if going_critical else 'Fleet backup runtime is adequate for short outages.'}",
                ],
            },
            ScenarioType.battery_degradation: {
                "title": "Battery SoH Drops to 85%",
                "description": "Battery State-of-Health degrades to 85%, reducing effective capacity by 15%. Simulates the cascading impact on runtime, health scores, and failure probability across the fleet.",
                "recommendations": [
                    "Immediately schedule capacity testing for all batteries.",
                    "Replace batteries with SoH < 80% — they are a critical liability.",
                    "Increase monitoring frequency for units already in warning/critical state.",
                    "Review maintenance contracts and spare battery inventory.",
                ],
            },
        }
        return meta[scenario_type]
