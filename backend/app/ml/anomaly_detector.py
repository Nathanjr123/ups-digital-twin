"""
Anomaly Detection Model
Uses Isolation Forest to detect abnormal patterns in UPS telemetry data.
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import joblib
from typing import Dict, Tuple, List
from pathlib import Path


class AnomalyDetector:
    """Detect anomalies in UPS sensor data using Isolation Forest."""
    
    def __init__(self, contamination: float = 0.1):
        """
        Initialize anomaly detector.
        
        Args:
            contamination: Expected proportion of anomalies in dataset (0.05-0.2)
        """
        self.contamination = contamination
        self.model = IsolationForest(
            contamination=contamination,
            random_state=42,
            n_estimators=100
        )
        self.scaler = StandardScaler()
        self.feature_names = []
        self.is_trained = False
        
    def _prepare_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Extract and prepare features for anomaly detection."""
        features = [
            "input_voltage",
            "output_voltage",
            "battery_voltage",
            "battery_soc",
            "battery_temperature",
            "inverter_temperature",
            "load_percentage",
            "runtime_remaining"
        ]
        
        self.feature_names = features
        return data[features]
    
    def train(self, training_data: pd.DataFrame) -> Dict:
        """
        Train the anomaly detection model.
        
        Args:
            training_data: Historical UPS data with normal operation
            
        Returns:
            Training metrics
        """
        X = self._prepare_features(training_data)
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Train model
        self.model.fit(X_scaled)
        self.is_trained = True
        
        # Evaluate on training data
        predictions = self.model.predict(X_scaled)
        anomaly_count = (predictions == -1).sum()
        
        return {
            "samples_trained": len(X),
            "anomalies_detected": int(anomaly_count),
            "contamination": self.contamination,
            "features": self.feature_names
        }
    
    def detect_anomaly(self, data_point: Dict) -> Dict:
        """
        Detect if a single data point is anomalous.
        
        Args:
            data_point: UPS telemetry reading
            
        Returns:
            Anomaly detection result with score and contributing factors
        """
        if not self.is_trained:
            raise ValueError("Model not trained. Call train() first.")
        
        # Convert to DataFrame for feature extraction
        df = pd.DataFrame([data_point])
        X = self._prepare_features(df)
        X_scaled = self.scaler.transform(X)
        
        # Predict
        prediction = self.model.predict(X_scaled)[0]
        anomaly_score = self.model.decision_function(X_scaled)[0]
        
        is_anomaly = prediction == -1
        
        # Identify contributing factors (features that deviate most)
        contributing_factors = self._identify_contributing_factors(X.iloc[0])
        
        return {
            "is_anomaly": bool(is_anomaly),
            "anomaly_score": float(anomaly_score),
            "confidence": self._score_to_confidence(anomaly_score),
            "contributing_factors": contributing_factors,
            "severity": self._determine_severity(anomaly_score)
        }
    
    def detect_batch(self, data: pd.DataFrame) -> List[Dict]:
        """Detect anomalies in batch of data points."""
        if not self.is_trained:
            raise ValueError("Model not trained. Call train() first.")
        
        X = self._prepare_features(data)
        X_scaled = self.scaler.transform(X)
        
        predictions = self.model.predict(X_scaled)
        scores = self.model.decision_function(X_scaled)
        
        results = []
        for i, (pred, score) in enumerate(zip(predictions, scores)):
            results.append({
                "index": i,
                "is_anomaly": bool(pred == -1),
                "anomaly_score": float(score),
                "confidence": self._score_to_confidence(score),
                "severity": self._determine_severity(score)
            })
        
        return results
    
    def _identify_contributing_factors(self, data_point: pd.Series) -> List[Dict]:
        """Identify which features contribute most to anomaly."""
        factors = []
        
        # Compare each feature to typical ranges
        feature_ranges = {
            "input_voltage": (220, 240),
            "output_voltage": (225, 235),
            "battery_voltage": (48, 54),
            "battery_soc": (90, 100),
            "battery_temperature": (20, 30),
            "inverter_temperature": (30, 50),
            "load_percentage": (30, 75),
            "runtime_remaining": (60, 180)
        }
        
        for feature, (low, high) in feature_ranges.items():
            if feature in data_point.index:
                value = data_point[feature]
                
                if value < low:
                    deviation = ((low - value) / low) * 100
                    factors.append({
                        "feature": feature,
                        "value": float(value),
                        "expected_range": f"{low}-{high}",
                        "deviation_pct": round(deviation, 2),
                        "status": "below_normal"
                    })
                elif value > high:
                    deviation = ((value - high) / high) * 100
                    factors.append({
                        "feature": feature,
                        "value": float(value),
                        "expected_range": f"{low}-{high}",
                        "deviation_pct": round(deviation, 2),
                        "status": "above_normal"
                    })
        
        # Sort by deviation
        factors.sort(key=lambda x: x["deviation_pct"], reverse=True)
        
        return factors[:3]  # Return top 3 contributors
    
    def _score_to_confidence(self, score: float) -> float:
        """Convert anomaly score to confidence percentage."""
        # Isolation Forest scores are typically between -1 and 1
        # More negative = more anomalous
        confidence = min(100, max(0, (1 - abs(score)) * 100))
        return round(confidence, 2)
    
    def _determine_severity(self, score: float) -> str:
        """Determine severity level based on anomaly score."""
        if score > -0.1:
            return "info"
        elif score > -0.3:
            return "warning"
        elif score > -0.5:
            return "high"
        else:
            return "critical"
    
    def save_model(self, path: str):
        """Save trained model to disk."""
        if not self.is_trained:
            raise ValueError("Cannot save untrained model")
        
        model_path = Path(path)
        model_path.parent.mkdir(parents=True, exist_ok=True)
        
        joblib.dump({
            "model": self.model,
            "scaler": self.scaler,
            "feature_names": self.feature_names,
            "contamination": self.contamination
        }, model_path)
    
    def load_model(self, path: str):
        """Load trained model from disk."""
        data = joblib.load(path)
        self.model = data["model"]
        self.scaler = data["scaler"]
        self.feature_names = data["feature_names"]
        self.contamination = data["contamination"]
        self.is_trained = True
