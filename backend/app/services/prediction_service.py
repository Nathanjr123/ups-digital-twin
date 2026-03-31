"""
Prediction Service
Handles ML model inference for anomaly detection and failure prediction.
"""

from typing import Dict, List, Optional
from datetime import datetime

from app.ml.anomaly_detector import AnomalyDetector
from app.ml.failure_predictor import FailurePredictor
from app.models.prediction import (
    AnomalyPrediction,
    FailurePrediction,
    CombinedPrediction,
    ContributingFactor,
    ModelPerformance
)
from app.models.ups import UPSTelemetry


class PredictionService:
    """Service for ML predictions."""
    
    def __init__(
        self,
        anomaly_detector: AnomalyDetector,
        failure_predictor: FailurePredictor
    ):
        self.anomaly_detector = anomaly_detector
        self.failure_predictor = failure_predictor
        self.prediction_cache: Dict[str, CombinedPrediction] = {}
        
    def predict_anomaly(self, telemetry: UPSTelemetry) -> AnomalyPrediction:
        """Detect anomalies in UPS telemetry."""
        data_point = telemetry.model_dump()
        
        result = self.anomaly_detector.detect_anomaly(data_point)
        
        # Convert contributing factors
        factors = [
            ContributingFactor(**factor)
            for factor in result["contributing_factors"]
        ]
        
        return AnomalyPrediction(
            ups_id=telemetry.ups_id,
            timestamp=datetime.now(),
            is_anomaly=result["is_anomaly"],
            anomaly_score=result["anomaly_score"],
            confidence=result["confidence"],
            severity=result["severity"],
            contributing_factors=factors
        )
    
    def predict_failure(self, telemetry: UPSTelemetry) -> FailurePrediction:
        """Predict UPS failure."""
        data_point = telemetry.model_dump()
        
        result = self.failure_predictor.predict_failure(data_point)
        
        # Convert risk factors
        factors = [
            ContributingFactor(**factor)
            for factor in result["risk_factors"]
        ]
        
        return FailurePrediction(
            ups_id=telemetry.ups_id,
            timestamp=datetime.now(),
            will_fail=result["will_fail"],
            failure_probability=result["failure_probability"],
            confidence=result["confidence"],
            time_to_failure_days=result["time_to_failure_days"],
            risk_level=result["risk_level"],
            risk_factors=factors,
            prediction_horizon=result["prediction_horizon"]
        )
    
    def predict_combined(self, telemetry: UPSTelemetry) -> CombinedPrediction:
        """Run both anomaly detection and failure prediction."""
        anomaly = self.predict_anomaly(telemetry)
        failure = self.predict_failure(telemetry)
        
        # Calculate overall risk score (0-100)
        risk_score = self._calculate_overall_risk(anomaly, failure)
        
        combined = CombinedPrediction(
            ups_id=telemetry.ups_id,
            timestamp=datetime.now(),
            anomaly=anomaly,
            failure=failure,
            overall_risk_score=risk_score
        )
        
        # Cache the prediction
        self.prediction_cache[telemetry.ups_id] = combined
        
        return combined
    
    def get_cached_prediction(self, ups_id: str) -> Optional[CombinedPrediction]:
        """Get last cached prediction for UPS."""
        return self.prediction_cache.get(ups_id)
    
    def predict_batch(self, telemetry_list: List[UPSTelemetry]) -> List[CombinedPrediction]:
        """Run predictions for multiple UPS units."""
        predictions = []
        
        for telemetry in telemetry_list:
            prediction = self.predict_combined(telemetry)
            predictions.append(prediction)
        
        return predictions
    
    def get_model_performance(self) -> List[ModelPerformance]:
        """Get performance metrics for all models."""
        performances = []
        
        # Anomaly detector performance
        if self.anomaly_detector.is_trained:
            anomaly_perf = ModelPerformance(
                model_name="anomaly_detector",
                samples_trained=0,  # Would track this in real implementation
                last_trained=datetime.now(),
                feature_importance={}
            )
            performances.append(anomaly_perf)
        
        # Failure predictor performance
        if self.failure_predictor.is_trained:
            feature_importance = self.failure_predictor.get_feature_importance()
            
            failure_perf = ModelPerformance(
                model_name="failure_predictor",
                accuracy=0.92,  # Would get from actual metrics
                precision=0.89,
                recall=0.87,
                f1_score=0.88,
                samples_trained=0,
                last_trained=datetime.now(),
                feature_importance=feature_importance
            )
            performances.append(failure_perf)
        
        return performances
    
    def _calculate_overall_risk(
        self,
        anomaly: AnomalyPrediction,
        failure: FailurePrediction
    ) -> float:
        """Calculate overall risk score combining anomaly and failure predictions."""
        # Weight failure prediction more heavily
        failure_weight = 0.7
        anomaly_weight = 0.3
        
        # Normalize failure probability to 0-100
        failure_score = failure.failure_probability * 100
        
        # Convert anomaly score to 0-100 scale
        # Anomaly scores are negative, more negative = more anomalous
        anomaly_score = min(100, max(0, abs(anomaly.anomaly_score) * 100))
        
        overall = (failure_score * failure_weight) + (anomaly_score * anomaly_weight)
        
        return round(overall, 2)
