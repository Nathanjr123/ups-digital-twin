"""
Main FastAPI Application
UPS Digital Twin API Server
"""

import logging
import os
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.core.config import get_settings
from app.api.routes import ups, predictions, alerts, simulation
from app.services.ups_service import UPSService
from app.services.prediction_service import PredictionService
from app.services.alert_service import AlertService
from app.services.websocket_service import WebSocketManager
from app.services.simulation_service import SimulationService
from app.ml.model_trainer import train_models_on_startup

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global service instances
ups_service: UPSService = None
prediction_service: PredictionService = None
alert_service: AlertService = None
websocket_manager: WebSocketManager = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info("Starting UPS Digital Twin API...")
    
    # Train/load ML models
    logger.info("Initializing ML models...")
    trainer = train_models_on_startup()
    models = trainer.get_models()
    
    # Initialize services
    global ups_service, prediction_service, alert_service, websocket_manager

    ups_service = UPSService()

    prediction_service = PredictionService(
        anomaly_detector=models["anomaly_detector"],
        failure_predictor=models["failure_predictor"]
    )
    alert_service = AlertService()
    
    # Initialize WebSocket manager
    settings = get_settings()
    websocket_manager = WebSocketManager(
        ups_service=ups_service,
        prediction_service=prediction_service,
        alert_service=alert_service,
        update_interval=settings.telemetry_update_interval
    )
    
    # Initialize simulation service
    simulation_service = SimulationService(ups_service, prediction_service)

    # Initialize route dependencies
    predictions.init_prediction_routes(prediction_service, ups_service)
    alerts.init_alert_routes(alert_service)
    simulation.init_simulation_routes(simulation_service)
    
    logger.info("API started successfully!")
    
    yield
    
    # Shutdown
    logger.info("Shutting down UPS Digital Twin API...")


# Create FastAPI app
settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(ups.router, prefix=settings.api_prefix)
app.include_router(predictions.router, prefix=settings.api_prefix)
app.include_router(alerts.router, prefix=settings.api_prefix)
app.include_router(simulation.router, prefix=settings.api_prefix)


# WebSocket endpoints
@app.websocket("/ws/telemetry")
async def websocket_telemetry(websocket: WebSocket):
    """WebSocket endpoint for real-time telemetry streaming."""
    await websocket_manager.connect_telemetry(websocket)
    
    try:
        while True:
            # Keep connection alive and handle client messages
            data = await websocket.receive_text()
            # Echo back for heartbeat
            await websocket.send_text(f"pong: {data}")
    
    except WebSocketDisconnect:
        websocket_manager.disconnect_telemetry(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        websocket_manager.disconnect_telemetry(websocket)


@app.websocket("/ws/alerts")
async def websocket_alerts(websocket: WebSocket):
    """WebSocket endpoint for real-time alert notifications."""
    await websocket_manager.connect_alerts(websocket)
    
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"pong: {data}")
    
    except WebSocketDisconnect:
        websocket_manager.disconnect_alerts(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        websocket_manager.disconnect_alerts(websocket)


# Serve frontend static files if they exist (production build)
STATIC_DIR = Path(__file__).parent.parent / "static"

if STATIC_DIR.exists():
    app.mount("/assets", StaticFiles(directory=str(STATIC_DIR / "assets")), name="static-assets")

    @app.get("/")
    async def serve_index():
        return FileResponse(str(STATIC_DIR / "index.html"))

    # Catch-all for client-side routing (React Router)
    @app.get("/{path:path}")
    async def serve_spa(path: str):
        # Don't intercept API, WebSocket, or health routes
        if path.startswith(("api/", "ws/", "health", "docs", "openapi.json", "redoc")):
            return
        file_path = STATIC_DIR / path
        if file_path.exists() and file_path.is_file():
            return FileResponse(str(file_path))
        return FileResponse(str(STATIC_DIR / "index.html"))
else:
    @app.get("/")
    async def root():
        """API root endpoint."""
        return {
            "name": settings.app_name,
            "version": settings.app_version,
            "status": "operational",
            "endpoints": {
                "ups": f"{settings.api_prefix}/ups",
                "predictions": f"{settings.api_prefix}/predictions",
                "alerts": f"{settings.api_prefix}/alerts",
                "websocket_telemetry": "/ws/telemetry",
                "websocket_alerts": "/ws/alerts"
            }
        }


# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "services": {
            "ups_service": ups_service is not None,
            "prediction_service": prediction_service is not None,
            "alert_service": alert_service is not None,
            "websocket_manager": websocket_manager is not None
        }
    }


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=settings.debug
    )
