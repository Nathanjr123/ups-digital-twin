"""
Model Trainer
Handles training and persistence of all ML models.
"""

from pathlib import Path
import logging
from typing import Dict

from app.ml.data_generator import FleetDataGenerator
from app.ml.anomaly_detector import AnomalyDetector
from app.ml.failure_predictor import FailurePredictor

logger = logging.getLogger(__name__)


class ModelTrainer:
    """Train and manage all ML models."""
    
    def __init__(self, models_dir: str = "./models"):
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(parents=True, exist_ok=True)
        
        self.anomaly_detector = AnomalyDetector(contamination=0.1)
        self.failure_predictor = FailurePredictor()
        
        self.fleet_generator = FleetDataGenerator()
        
    def train_all_models(self, days_of_data: int = 90) -> Dict:
        """
        Train all ML models with synthetic historical data.
        
        Args:
            days_of_data: Number of days of historical data to generate
            
        Returns:
            Training results for all models
        """
        logger.info(f"Generating {days_of_data} days of historical data...")
        
        # Generate historical data
        historical_data = self.fleet_generator.generate_historical_data(days=days_of_data)
        
        logger.info(f"Generated {len(historical_data)} data points")
        
        # Train anomaly detector on normal operation data
        logger.info("Training anomaly detector...")
        normal_data = historical_data[historical_data["status"] == "normal"]
        anomaly_metrics = self.anomaly_detector.train(normal_data)
        
        logger.info(f"Anomaly detector trained: {anomaly_metrics}")
        
        # Train failure predictor on all data
        logger.info("Training failure predictor...")
        failure_metrics = self.failure_predictor.train(historical_data)
        
        logger.info(f"Failure predictor trained: {failure_metrics}")
        
        # Save models
        logger.info("Saving models...")
        self.save_models()
        
        return {
            "anomaly_detection": anomaly_metrics,
            "failure_prediction": failure_metrics,
            "training_data_size": len(historical_data),
            "models_saved": True
        }
    
    def save_models(self):
        """Save all trained models to disk."""
        anomaly_path = self.models_dir / "anomaly_detector.joblib"
        failure_path = self.models_dir / "failure_predictor.joblib"
        
        self.anomaly_detector.save_model(str(anomaly_path))
        self.failure_predictor.save_model(str(failure_path))
        
        logger.info(f"Models saved to {self.models_dir}")
    
    def load_models(self):
        """Load pre-trained models from disk."""
        anomaly_path = self.models_dir / "anomaly_detector.joblib"
        failure_path = self.models_dir / "failure_predictor.joblib"
        
        if not anomaly_path.exists() or not failure_path.exists():
            raise FileNotFoundError("Model files not found. Train models first.")
        
        self.anomaly_detector.load_model(str(anomaly_path))
        self.failure_predictor.load_model(str(failure_path))
        
        logger.info("Models loaded successfully")
    
    def get_models(self):
        """Get the trained model instances."""
        return {
            "anomaly_detector": self.anomaly_detector,
            "failure_predictor": self.failure_predictor
        }


def train_models_on_startup():
    """Train models on application startup if they don't exist."""
    trainer = ModelTrainer()
    
    models_path = Path("./models")
    anomaly_path = models_path / "anomaly_detector.joblib"
    failure_path = models_path / "failure_predictor.joblib"
    
    # Check if models exist
    if not anomaly_path.exists() or not failure_path.exists():
        logger.info("Models not found. Training new models...")
        results = trainer.train_all_models(days_of_data=90)
        logger.info(f"Training complete: {results}")
        return trainer
    else:
        logger.info("Loading existing models...")
        trainer.load_models()
        return trainer
