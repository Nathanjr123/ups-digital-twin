"""
Simulation Routes
Strategy mode and what-if scenario API endpoints.
"""

from fastapi import APIRouter, HTTPException
from app.models.simulation import (
    StrategySettings, StrategyImpact,
    SimulationRequest, SimulationResult,
)

router = APIRouter(prefix="/simulation", tags=["simulation"])

_simulation_service = None


def init_simulation_routes(simulation_service):
    global _simulation_service
    _simulation_service = simulation_service


@router.get("/strategy", response_model=StrategySettings)
async def get_strategy():
    """Get current strategy settings."""
    if _simulation_service is None:
        raise HTTPException(status_code=503, detail="Simulation service not ready")
    return _simulation_service.get_strategy()


@router.post("/strategy", response_model=StrategyImpact)
async def set_strategy(settings: StrategySettings):
    """Set strategy mode and aggressiveness, returns projected impact."""
    if _simulation_service is None:
        raise HTTPException(status_code=503, detail="Simulation service not ready")
    return _simulation_service.set_strategy(settings)


@router.post("/strategy/preview", response_model=StrategyImpact)
async def preview_strategy(settings: StrategySettings):
    """Preview strategy impact without persisting it."""
    if _simulation_service is None:
        raise HTTPException(status_code=503, detail="Simulation service not ready")
    return _simulation_service.compute_strategy_impact(settings)


@router.post("/run", response_model=SimulationResult)
async def run_simulation(request: SimulationRequest):
    """Run a what-if scenario simulation against current fleet telemetry."""
    if _simulation_service is None:
        raise HTTPException(status_code=503, detail="Simulation service not ready")
    try:
        return _simulation_service.run_scenario(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
