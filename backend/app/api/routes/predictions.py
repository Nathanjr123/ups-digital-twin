"""
Prediction API Routes
Endpoints for ML predictions and model analytics.
"""

from fastapi import APIRouter, HTTPException
from typing import List

from app.models.prediction import CombinedPrediction, ModelPerformance
from app.services.prediction_service import PredictionService
from app.services.ups_service import UPSService

router = APIRouter(prefix="/predictions", tags=["Predictions"])

# Services will be initialized in main app
prediction_service: PredictionService = None
ups_service: UPSService = None


def init_prediction_routes(pred_service: PredictionService, u_service: UPSService):
    """Initialize routes with service instances."""
    global prediction_service, ups_service
    prediction_service = pred_service
    ups_service = u_service


@router.get("/{ups_id}", response_model=CombinedPrediction)
async def get_predictions(ups_id: str):
    """Get current predictions for a specific UPS."""
    # Get latest telemetry
    telemetry = ups_service.get_latest_telemetry(ups_id)
    
    if not telemetry:
        raise HTTPException(status_code=404, detail=f"UPS {ups_id} not found")
    
    # Run predictions
    prediction = prediction_service.predict_combined(telemetry)
    
    return prediction


@router.post("/run", response_model=List[CombinedPrediction])
async def run_predictions():
    """Run predictions for all UPS units in the fleet."""
    # Get all current telemetry
    telemetry_list = ups_service.generate_fleet_snapshot()
    
    # Run batch predictions
    predictions = prediction_service.predict_batch(telemetry_list)
    
    return predictions


@router.get("/analytics/model-performance", response_model=List[ModelPerformance])
async def get_model_performance():
    """Get ML model performance metrics."""
    return prediction_service.get_model_performance()
