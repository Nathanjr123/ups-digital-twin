"""
Pydantic Models for Predictions
Defines data structures for ML predictions and analysis.
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Literal, Optional


class ContributingFactor(BaseModel):
    """Factor contributing to anomaly or failure risk."""
    
    feature: str
    value: float
    expected_range: Optional[str] = None
    deviation_pct: Optional[float] = None
    importance: Optional[float] = None
    status: Literal["normal", "below_normal", "above_normal", "high_risk"]


class AnomalyPrediction(BaseModel):
    """Anomaly detection result."""
    
    ups_id: str
    timestamp: datetime
    is_anomaly: bool
    anomaly_score: float = Field(..., description="Anomaly score (more negative = more anomalous)")
    confidence: float = Field(..., ge=0, le=100, description="Confidence percentage")
    severity: Literal["info", "warning", "high", "critical"]
    contributing_factors: list[ContributingFactor] = Field(default_factory=list)
    
    class Config:
        json_schema_extra = {
            "example": {
                "ups_id": "UPS-001",
                "timestamp": "2024-03-26T10:30:00",
                "is_anomaly": True,
                "anomaly_score": -0.42,
                "confidence": 85.5,
                "severity": "warning",
                "contributing_factors": [
                    {
                        "feature": "battery_temperature",
                        "value": 38.5,
                        "expected_range": "20-30",
                        "deviation_pct": 28.3,
                        "status": "above_normal"
                    }
                ]
            }
        }


class FailurePrediction(BaseModel):
    """Failure prediction result."""
    
    ups_id: str
    timestamp: datetime
    will_fail: bool
    failure_probability: float = Field(..., ge=0, le=1, description="Probability of failure (0-1)")
    confidence: float = Field(..., ge=0, le=100, description="Confidence percentage")
    time_to_failure_days: int = Field(..., ge=0, description="Estimated days until failure")
    risk_level: Literal["low", "medium", "high", "critical"]
    risk_factors: list[ContributingFactor] = Field(default_factory=list)
    prediction_horizon: str = Field(default="7_days", description="Prediction window")
    
    class Config:
        json_schema_extra = {
            "example": {
                "ups_id": "UPS-009",
                "timestamp": "2024-03-26T10:30:00",
                "will_fail": True,
                "failure_probability": 0.78,
                "confidence": 92.3,
                "time_to_failure_days": 5,
                "risk_level": "high",
                "risk_factors": [
                    {
                        "feature": "battery_soc",
                        "value": 65.0,
                        "importance": 0.23,
                        "status": "high_risk"
                    }
                ],
                "prediction_horizon": "7_days"
            }
        }


class CombinedPrediction(BaseModel):
    """Combined anomaly and failure prediction."""
    
    ups_id: str
    timestamp: datetime
    anomaly: AnomalyPrediction
    failure: FailurePrediction
    overall_risk_score: float = Field(..., ge=0, le=100, description="Combined risk score")
    
    class Config:
        json_schema_extra = {
            "example": {
                "ups_id": "UPS-009",
                "timestamp": "2024-03-26T10:30:00",
                "anomaly": {},
                "failure": {},
                "overall_risk_score": 78.5
            }
        }


class ModelPerformance(BaseModel):
    """ML model performance metrics."""
    
    model_name: str
    accuracy: Optional[float] = None
    precision: Optional[float] = None
    recall: Optional[float] = None
    f1_score: Optional[float] = None
    samples_trained: int
    last_trained: datetime
    feature_importance: dict[str, float] = Field(default_factory=dict)
    
    class Config:
        json_schema_extra = {
            "example": {
                "model_name": "failure_predictor",
                "accuracy": 0.92,
                "precision": 0.89,
                "recall": 0.87,
                "f1_score": 0.88,
                "samples_trained": 25920,
                "last_trained": "2024-03-26T00:00:00",
                "feature_importance": {
                    "battery_soc": 0.23,
                    "battery_temperature": 0.18,
                    "thermal_stress": 0.15
                }
            }
        }


class PredictionHistory(BaseModel):
    """Historical predictions for a UPS."""
    
    ups_id: str
    start_time: datetime
    end_time: datetime
    predictions: list[CombinedPrediction]
    
    class Config:
        json_schema_extra = {
            "example": {
                "ups_id": "UPS-009",
                "start_time": "2024-03-20T00:00:00",
                "end_time": "2024-03-26T23:59:59",
                "predictions": []
            }
        }
