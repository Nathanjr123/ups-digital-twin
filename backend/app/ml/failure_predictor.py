"""
Failure Prediction Model
Uses Random Forest to predict UPS failures and estimate time to failure.
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import joblib
from typing import Dict, Tuple, List
from pathlib import Path
from datetime import datetime, timedelta


class FailurePredictor:
    """Predict UPS failures using machine learning."""
    
    def __init__(self):
        self.model = RandomForestClassifier(
            n_estimators=200,
            max_depth=15,
            random_state=42,
            class_weight="balanced"
        )
        self.scaler = StandardScaler()
        self.feature_names = []
        self.is_trained = False
        self.feature_importance = {}
        
    def _engineer_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Create features for failure prediction."""
        features = data.copy()
        
        # Basic sensor features
        base_features = [
            "input_voltage",
            "output_voltage",
            "battery_voltage",
            "battery_soc",
            "battery_temperature",
            "battery_current",
            "inverter_temperature",
            "load_percentage",
            "runtime_remaining",
            "ambient_temperature"
        ]
        
        # Engineered features
        features["voltage_stability"] = features["output_voltage"] / features["input_voltage"]
        features["thermal_stress"] = features["battery_temperature"] + features["inverter_temperature"]
        features["battery_health_proxy"] = features["battery_voltage"] * features["battery_soc"]
        features["load_to_runtime_ratio"] = features["load_percentage"] / (features["runtime_remaining"] + 1)
        
        # Temperature differentials
        features["inverter_temp_diff"] = features["inverter_temperature"] - features["ambient_temperature"]
        features["battery_temp_diff"] = features["battery_temperature"] - features["ambient_temperature"]
        
        # Risk indicators
        features["low_battery_risk"] = (features["battery_soc"] < 80).astype(int)
        features["high_temp_risk"] = (features["battery_temperature"] > 35).astype(int)
        features["overload_risk"] = (features["load_percentage"] > 85).astype(int)
        
        self.feature_names = base_features + [
            "voltage_stability",
            "thermal_stress",
            "battery_health_proxy",
            "load_to_runtime_ratio",
            "inverter_temp_diff",
            "battery_temp_diff",
            "low_battery_risk",
            "high_temp_risk",
            "overload_risk"
        ]
        
        return features[self.feature_names]
    
    def _create_labels(self, data: pd.DataFrame, failure_window_days: int = 7) -> np.ndarray:
        """
        Create failure labels based on status.
        
        Args:
            data: UPS telemetry data
            failure_window_days: Days before failure to mark as positive
            
        Returns:
            Binary labels (1 = will fail soon, 0 = normal)
        """
        # In real scenario, we'd look ahead to see if failure occurs
        # For synthetic data, use status as proxy
        labels = []
        
        for _, row in data.iterrows():
            status = row.get("status", "normal")
            
            if status in ["critical", "failure"]:
                labels.append(1)
            elif status == "warning":
                # Some warnings lead to failure
                labels.append(np.random.choice([0, 1], p=[0.7, 0.3]))
            else:
                labels.append(0)
        
        return np.array(labels)
    
    def train(self, training_data: pd.DataFrame) -> Dict:
        """
        Train the failure prediction model.
        
        Args:
            training_data: Historical UPS data with various states
            
        Returns:
            Training metrics and performance
        """
        # Prepare features
        X = self._engineer_features(training_data)
        y = self._create_labels(training_data)
        

        # CLEAN DATA
        X = np.where(np.isinf(X), np.nan, X)

        col_medians = np.nanmedian(X, axis=0)
        inds = np.where(np.isnan(X))
        X[inds] = np.take(col_medians, inds[1])

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train model
        self.model.fit(X_train_scaled, y_train)
        self.is_trained = True
        
        # Evaluate
        y_pred = self.model.predict(X_test_scaled)
        y_pred_proba = self.model.predict_proba(X_test_scaled)[:, 1]
        
        # Feature importance
        self.feature_importance = dict(zip(
            self.feature_names,
            self.model.feature_importances_
        ))
        
        # Metrics
        accuracy = accuracy_score(y_test, y_pred)
        conf_matrix = confusion_matrix(y_test, y_pred)
        
        return {
            "samples_trained": len(X_train),
            "samples_tested": len(X_test),
            "accuracy": float(accuracy),
            "confusion_matrix": conf_matrix.tolist(),
            "feature_importance": {
                k: float(v) for k, v in sorted(
                    self.feature_importance.items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:10]  # Top 10 features
            },
            "positive_samples": int(y.sum()),
            "negative_samples": int(len(y) - y.sum())
        }
    
    def predict_failure(self, data_point: Dict) -> Dict:
        """
        Predict failure for a single UPS reading.
        
        Args:
            data_point: Current UPS telemetry
            
        Returns:
            Prediction with probability, time estimate, and risk factors
        """
        if not self.is_trained:
            raise ValueError("Model not trained. Call train() first.")
        
        # Convert to DataFrame
        df = pd.DataFrame([data_point])
        X = self._engineer_features(df)
        X_scaled = self.scaler.transform(X)
        
        # Predict
        prediction = self.model.predict(X_scaled)[0]
        probability = self.model.predict_proba(X_scaled)[0]
        
        failure_probability = float(probability[1])
        
        # Estimate time to failure based on probability and current metrics
        time_to_failure = self._estimate_time_to_failure(
            failure_probability,
            data_point
        )
        
        # Identify risk factors
        risk_factors = self._identify_risk_factors(X.iloc[0])
        
        # Determine risk level
        risk_level = self._determine_risk_level(failure_probability)
        
        return {
            "will_fail": bool(prediction == 1),
            "failure_probability": round(failure_probability, 4),
            "confidence": round(max(probability) * 100, 2),
            "time_to_failure_days": time_to_failure,
            "risk_level": risk_level,
            "risk_factors": risk_factors,
            "prediction_horizon": "7_days"
        }
    
    def predict_batch(self, data: pd.DataFrame) -> List[Dict]:
        """Predict failures for batch of data."""
        if not self.is_trained:
            raise ValueError("Model not trained. Call train() first.")
        
        X = self._engineer_features(data)
        X_scaled = self.scaler.transform(X)
        
        predictions = self.model.predict(X_scaled)
        probabilities = self.model.predict_proba(X_scaled)
        
        results = []
        for i, (pred, prob) in enumerate(zip(predictions, probabilities)):
            results.append({
                "index": i,
                "will_fail": bool(pred == 1),
                "failure_probability": round(float(prob[1]), 4),
                "confidence": round(float(max(prob)) * 100, 2),
                "risk_level": self._determine_risk_level(prob[1])
            })
        
        return results
    
    def _estimate_time_to_failure(self, probability: float, data_point: Dict) -> int:
        """
        Estimate days until failure based on probability and current state.
        
        Args:
            probability: Failure probability (0-1)
            data_point: Current UPS state
            
        Returns:
            Estimated days until failure
        """
        # Base estimate from probability
        if probability < 0.3:
            base_days = 30
        elif probability < 0.5:
            base_days = 14
        elif probability < 0.7:
            base_days = 7
        elif probability < 0.9:
            base_days = 3
        else:
            base_days = 1
        
        # Adjust based on specific metrics
        battery_soc = data_point.get("battery_soc", 100)
        battery_temp = data_point.get("battery_temperature", 25)
        
        if battery_soc < 70:
            base_days = max(1, int(base_days * 0.7))
        
        if battery_temp > 40:
            base_days = max(1, int(base_days * 0.8))
        
        return base_days
    
    def _identify_risk_factors(self, features: pd.Series) -> List[Dict]:
        """Identify the main contributors to failure risk."""
        factors = []
        
        # Check each feature against importance
        sorted_features = sorted(
            self.feature_importance.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]  # Top 5 important features
        
        for feature_name, importance in sorted_features:
            if feature_name in features.index:
                value = features[feature_name]
                
                # Determine if this feature is in risk range
                risk_status = self._assess_feature_risk(feature_name, value)
                
                if risk_status != "normal":
                    factors.append({
                        "feature": feature_name,
                        "value": float(value),
                        "importance": round(float(importance), 4),
                        "status": risk_status
                    })
        
        return factors
    
    def _assess_feature_risk(self, feature_name: str, value: float) -> str:
        """Assess if a feature value is in risk range."""
        risk_thresholds = {
            "battery_soc": (80, "below"),
            "battery_temperature": (35, "above"),
            "inverter_temperature": (55, "above"),
            "load_percentage": (85, "above"),
            "runtime_remaining": (60, "below"),
            "thermal_stress": (70, "above"),
            "battery_health_proxy": (4500, "below")
        }
        
        if feature_name in risk_thresholds:
            threshold, direction = risk_thresholds[feature_name]
            
            if direction == "below" and value < threshold:
                return "high_risk"
            elif direction == "above" and value > threshold:
                return "high_risk"
        
        return "normal"
    
    def _determine_risk_level(self, probability: float) -> str:
        """Determine risk level from failure probability."""
        if probability < 0.25:
            return "low"
        elif probability < 0.5:
            return "medium"
        elif probability < 0.75:
            return "high"
        else:
            return "critical"
    
    def get_feature_importance(self) -> Dict:
        """Get feature importance rankings."""
        if not self.is_trained:
            raise ValueError("Model not trained")
        
        return {
            k: float(v) for k, v in sorted(
                self.feature_importance.items(),
                key=lambda x: x[1],
                reverse=True
            )
        }
    
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
            "feature_importance": self.feature_importance
        }, model_path)
    
    def load_model(self, path: str):
        """Load trained model from disk."""
        data = joblib.load(path)
        self.model = data["model"]
        self.scaler = data["scaler"]
        self.feature_names = data["feature_names"]
        self.feature_importance = data["feature_importance"]
        self.is_trained = True
