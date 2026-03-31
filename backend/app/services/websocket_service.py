"""
WebSocket Service
Handles real-time data streaming to connected clients.
"""

import asyncio
import json
from typing import Set
from fastapi import WebSocket
import logging

from app.services.ups_service import UPSService
from app.services.prediction_service import PredictionService
from app.services.alert_service import AlertService

logger = logging.getLogger(__name__)


class WebSocketManager:
    """Manage WebSocket connections and broadcast updates."""
    
    def __init__(
        self,
        ups_service: UPSService,
        prediction_service: PredictionService,
        alert_service: AlertService,
        update_interval: int = 2
    ):
        self.ups_service = ups_service
        self.prediction_service = prediction_service
        self.alert_service = alert_service
        self.update_interval = update_interval
        
        self.telemetry_connections: Set[WebSocket] = set()
        self.alert_connections: Set[WebSocket] = set()
        self.is_streaming = False
        
    async def connect_telemetry(self, websocket: WebSocket):
        """Connect a new telemetry WebSocket client."""
        await websocket.accept()
        self.telemetry_connections.add(websocket)
        logger.info(f"Telemetry client connected. Total: {len(self.telemetry_connections)}")
        
        # Start streaming if not already running
        if not self.is_streaming:
            asyncio.create_task(self.stream_telemetry())
    
    def disconnect_telemetry(self, websocket: WebSocket):
        """Disconnect a telemetry WebSocket client."""
        self.telemetry_connections.discard(websocket)
        logger.info(f"Telemetry client disconnected. Total: {len(self.telemetry_connections)}")
    
    async def connect_alerts(self, websocket: WebSocket):
        """Connect a new alert WebSocket client."""
        await websocket.accept()
        self.alert_connections.add(websocket)
        logger.info(f"Alert client connected. Total: {len(self.alert_connections)}")
    
    def disconnect_alerts(self, websocket: WebSocket):
        """Disconnect an alert WebSocket client."""
        self.alert_connections.discard(websocket)
        logger.info(f"Alert client disconnected. Total: {len(self.alert_connections)}")
    
    async def stream_telemetry(self):
        """Stream telemetry data to all connected clients."""
        self.is_streaming = True
        logger.info("Starting telemetry stream...")
        
        try:
            while self.telemetry_connections:
                # Generate fleet snapshot
                telemetry_list = self.ups_service.generate_fleet_snapshot()
                
                # Convert to JSON
                data = {
                    "type": "telemetry_update",
                    "timestamp": telemetry_list[0].timestamp.isoformat() if telemetry_list else None,
                    "data": [t.model_dump(mode='json') for t in telemetry_list]
                }
                
                # Broadcast to all connected clients
                await self.broadcast_telemetry(data)
                
                # Run predictions periodically and check for new alerts
                if len(telemetry_list) > 0:
                    predictions = self.prediction_service.predict_batch(telemetry_list)
                    
                    # Process predictions to generate alerts
                    for prediction in predictions:
                        self.alert_service.process_prediction(prediction)
                
                # Wait before next update
                await asyncio.sleep(self.update_interval)
        
        except Exception as e:
            logger.error(f"Error in telemetry stream: {e}")
        
        finally:
            self.is_streaming = False
            logger.info("Telemetry stream stopped")
    
    async def broadcast_telemetry(self, data: dict):
        """Broadcast telemetry data to all connected clients."""
        if not self.telemetry_connections:
            return
        
        message = json.dumps(data)
        disconnected = set()
        
        for connection in self.telemetry_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"Error sending to client: {e}")
                disconnected.add(connection)
        
        # Remove disconnected clients
        for conn in disconnected:
            self.disconnect_telemetry(conn)
    
    async def broadcast_alert(self, alert_data: dict):
        """Broadcast new alert to all connected clients."""
        if not self.alert_connections:
            return
        
        data = {
            "type": "new_alert",
            "data": alert_data
        }
        
        message = json.dumps(data)
        disconnected = set()
        
        for connection in self.alert_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"Error sending alert to client: {e}")
                disconnected.add(connection)
        
        # Remove disconnected clients
        for conn in disconnected:
            self.disconnect_alerts(conn)
