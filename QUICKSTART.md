# UPS Digital Twin - Quick Start Guide

## 🎉 Project Complete!

Your production-quality UPS Digital Twin system is ready to run. This guide will get you started in 5 minutes.

## ✅ What You Have

**Complete Full-Stack Application:**
- ✅ Python FastAPI backend with ML models
- ✅ React TypeScript frontend with Tailwind CSS
- ✅ Real-time WebSocket streaming
- ✅ Machine learning models (Anomaly Detection + Failure Prediction)
- ✅ Synthetic data generator for 12 UPS units
- ✅ Complete Docker setup
- ✅ Professional UI with 5 pages

## 🚀 Fastest Way to Run (3 commands)

```bash
cd ups-digital-twin
docker-compose up --build
```

**Then open:** http://localhost

That's it! The system will:
1. Build both backend and frontend containers
2. Train ML models on startup (~30 seconds)
3. Start streaming real-time telemetry data
4. Launch the web interface

## 🖥️ What You'll See

### 1. Overview Dashboard (/)
- Fleet summary with 4 key metric cards
- Real-time status grid showing all 12 UPS units
- Recent alerts panel
- Live connection indicator

### 2. Fleet Monitoring (/fleet)
- Grid view of all UPS units
- Filter by status (healthy/warning/critical)
- Battery, load, and temperature metrics
- Click any unit for detailed view

### 3. UPS Detail Page (/ups/UPS-XXX)
- 4 circular gauges (Battery SOC, Load, Temperatures)
- Current metrics table
- Failure prediction with probability and timeline
- Risk factors and anomaly detection
- System metadata

### 4. Analytics (/analytics)
- ML model performance metrics
- Feature importance chart
- Model insights and recommendations

### 5. Alerts (/alerts)
- Real-time alert feed
- Filter by severity and status
- Acknowledge and resolve alerts
- Alert statistics

## 🎮 Demo Scenarios

The system generates realistic scenarios:

**UPS-009**: Battery degradation over 14 days → failure predicted
**UPS-011**: Overload condition → high temperature warnings
**UPS-012**: Cooling failure → progressive temperature rise
**Others**: Normal operation with occasional anomalies

## 📡 API Endpoints

**Backend API Docs:** http://localhost:8000/docs

Key endpoints:
- `GET /api/ups/` - List all UPS
- `GET /api/ups/fleet-summary` - Fleet stats
- `GET /api/predictions/{ups_id}` - ML predictions
- `GET /api/alerts/` - List alerts
- `WS /ws/telemetry` - Real-time stream

## 🛠️ Local Development (Without Docker)

### Backend:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend:
```bash
cd frontend
npm install
npm run dev
```

Access at: http://localhost:5173

## 📊 System Architecture

```
┌─────────────┐         WebSocket          ┌──────────────┐
│   Frontend  │◄──────────────────────────►│   Backend    │
│  React +TS  │         REST API            │  FastAPI     │
└─────────────┘                             └──────────────┘
                                                   │
                                            ┌──────┴──────┐
                                            │             │
                                      ┌─────▼─────┐ ┌────▼────┐
                                      │  Anomaly  │ │ Failure │
                                      │ Detector  │ │Predictor│
                                      └───────────┘ └─────────┘
                                            │
                                      ┌─────▼──────┐
                                      │  Synthetic │
                                      │    Data    │
                                      │ Generator  │
                                      └────────────┘
```

## 🔍 Project Structure

```
ups-digital-twin/
├── backend/               # Python FastAPI
│   ├── app/
│   │   ├── api/routes/   # REST endpoints
│   │   ├── ml/           # ML models
│   │   ├── services/     # Business logic
│   │   └── main.py       # App entry point
│   └── Dockerfile
├── frontend/              # React TypeScript
│   ├── src/
│   │   ├── components/   # UI components
│   │   ├── pages/        # Page views
│   │   ├── services/     # API client
│   │   └── hooks/        # WebSocket hook
│   └── Dockerfile
├── docker-compose.yml     # Orchestration
└── README.md             # Full documentation
```

## 💡 Key Features

### Real-Time Monitoring
- WebSocket streams telemetry every 2 seconds
- Live gauges and charts
- Automatic reconnection

### ML Predictions
- **Anomaly Detection**: Isolation Forest detects unusual patterns
- **Failure Prediction**: Random Forest predicts failures 7-14 days ahead
- **Risk Analysis**: Identifies contributing factors

### Professional UI
- Modern Tailwind CSS design
- Responsive layout (mobile/tablet/desktop)
- Interactive charts with Recharts
- Real-time updates without page refresh

### Alert System
- Automatic alert generation from predictions
- Severity-based prioritization
- Acknowledge/resolve workflow
- Recommended actions

## 🎯 Next Steps for Production

### For Real SCADA Integration:

1. **Replace Data Generator** (backend/app/ml/data_generator.py)
   - Add OPC-UA/Modbus/MQTT client
   - Connect to real sensors
   - Keep the same data structure

2. **Retrain Models** with historical data
   - Use actual failure records
   - Adjust thresholds based on real patterns

3. **Add Authentication**
   - JWT tokens
   - Role-based access control

4. **Deploy to Cloud**
   - AWS/Azure/GCP
   - Load balancing
   - Auto-scaling

## 🐛 Troubleshooting

**Port already in use:**
```bash
# Change ports in docker-compose.yml
ports:
  - "8001:8000"  # Backend
  - "81:80"      # Frontend
```

**Models training slow:**
- Normal on first run (~30 seconds)
- Models are cached after first training

**WebSocket not connecting:**
- Check backend is running: http://localhost:8000/health
- Check browser console for errors

**Frontend shows "Loading...":**
- Backend might still be training models
- Check backend logs: `docker-compose logs backend`

## 📚 Documentation

- **Full README**: `README.md` (comprehensive guide)
- **API Docs**: http://localhost:8000/docs (interactive Swagger)
- **Code Comments**: Extensive docstrings in all files

## 🎬 What to Demo

**For your client meeting:**

1. Start with Overview → Show fleet health
2. Filter Fleet → Demonstrate warning/critical units
3. Click UPS-009 → Show failure prediction (high probability)
4. Go to Analytics → Show model performance and feature importance
5. Open Alerts → Show real-time alert management
6. Toggle network off → Show reconnection
7. Open API docs → Show professional backend

## 💪 What This Demonstrates

✅ Full-stack development (Python + TypeScript)
✅ Machine learning engineering (training + inference)
✅ Real-time systems (WebSocket)
✅ System architecture (microservices)
✅ DevOps (Docker, containerization)
✅ UI/UX design (modern, professional)
✅ API design (RESTful + async)
✅ Data engineering (synthetic data generation)
✅ Production-ready code (error handling, logging)
✅ Documentation (comprehensive)

## 🚀 Ready to Impress!

Your system is production-quality and ready to showcase. The combination of:
- Real-time monitoring
- AI predictions
- Professional UI
- Complete documentation
- Docker deployment

...makes this a compelling demonstration of full-stack capabilities.

**Good luck with your meeting! 🎯**
