# UPS Digital Twin - AI-Enhanced Predictive Maintenance System

A production-quality digital twin system for UPS (Uninterruptible Power Supply) fleet monitoring with real-time telemetry, machine learning-based failure prediction, and anomaly detection.

## 🎯 Project Overview

This system demonstrates advanced capabilities in:
- **Real-time Monitoring**: WebSocket-based live telemetry streaming for 12 UPS units
- **Predictive Maintenance**: ML models predict failures 7-14 days in advance
- **Anomaly Detection**: Isolation Forest algorithm detects unusual operating patterns
- **Interactive Dashboard**: React-based UI with real-time updates and detailed analytics
- **Production Architecture**: Scalable, containerized deployment ready for industrial use

## 🏗️ Architecture

### Backend (Python/FastAPI)
- **Framework**: FastAPI with async/await support
- **ML Models**: 
  - Isolation Forest for anomaly detection
  - Random Forest for failure prediction
- **Data Generation**: Realistic synthetic UPS telemetry with various failure modes
- **Real-time Communication**: WebSocket for live data streaming
- **API Design**: RESTful endpoints for fleet management, predictions, and alerts

### Frontend (React/TypeScript)
- **Framework**: React 18 with TypeScript
- **Styling**: Tailwind CSS for modern, responsive design
- **Charts**: Recharts for data visualization
- **State Management**: React hooks with WebSocket integration
- **Routing**: React Router for SPA navigation

### ML Models
1. **Anomaly Detector** (Isolation Forest)
   - Detects abnormal patterns in real-time sensor data
   - Identifies contributing factors
   - Severity classification (info → warning → high → critical)

2. **Failure Predictor** (Random Forest Classifier)
   - Predicts failure probability within 7-day window
   - Estimates time to failure
   - Provides risk factor analysis
   - Feature importance tracking

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- (Optional) Python 3.11+ and Node.js 20+ for local development

### Running with Docker (Recommended)

1. **Clone and navigate to project**:
```bash
cd ups-digital-twin
```

2. **Build and start services**:
```bash
docker-compose up --build
```

3. **Access the application**:
   - Frontend: http://localhost
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

4. **Stop services**:
```bash
docker-compose down
```

### Local Development Setup

#### Backend Setup

1. **Navigate to backend directory**:
```bash
cd backend
```

2. **Create virtual environment**:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Run the server**:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The backend will automatically:
- Generate synthetic training data
- Train ML models on startup (if not already trained)
- Start streaming telemetry data

#### Frontend Setup

1. **Navigate to frontend directory**:
```bash
cd frontend
```

2. **Install dependencies**:
```bash
npm install
```

3. **Run development server**:
```bash
npm run dev
```

4. **Access at**: http://localhost:5173

## 📊 Features

### Dashboard Overview
- Fleet-wide summary statistics
- Real-time status grid for all UPS units
- Recent alerts and notifications
- Live connection status indicator

### Fleet Monitoring
- Grid view of all UPS units
- Filter by health status (healthy/warning/critical)
- Quick metrics: battery SOC, load %, temperature
- Click-through to detailed unit view

### UPS Detail View
- Real-time gauges for key metrics
- Current telemetry readings
- Failure prediction with probability and timeline
- Risk factor analysis
- System information and maintenance history

### Analytics
- ML model performance metrics
- Feature importance visualization
- Prediction insights and recommendations
- Model accuracy, precision, recall, F1 scores

### Alerts Management
- Real-time alert notifications
- Filter by severity and status
- Acknowledge and resolve alerts
- Recommended actions for each alert
- Alert statistics dashboard

## 🔧 API Endpoints

### UPS Endpoints
- `GET /api/ups/` - List all UPS units
- `GET /api/ups/fleet-summary` - Fleet statistics
- `GET /api/ups/{ups_id}` - Specific UPS details
- `GET /api/ups/{ups_id}/telemetry` - Latest telemetry
- `GET /api/ups/{ups_id}/history` - Historical data

### Prediction Endpoints
- `GET /api/predictions/{ups_id}` - Get predictions for UPS
- `POST /api/predictions/run` - Run predictions for all units
- `GET /api/predictions/analytics/model-performance` - Model metrics

### Alert Endpoints
- `GET /api/alerts/` - List alerts (filterable)
- `GET /api/alerts/statistics` - Alert statistics
- `GET /api/alerts/{alert_id}` - Specific alert
- `PATCH /api/alerts/{alert_id}` - Update alert status

### WebSocket Endpoints
- `WS /ws/telemetry` - Real-time telemetry stream
- `WS /ws/alerts` - Real-time alert notifications

## 🎨 Technology Stack

### Backend
- **FastAPI** - Modern, fast web framework
- **Pydantic** - Data validation
- **scikit-learn** - ML algorithms
- **pandas/numpy** - Data processing
- **uvicorn** - ASGI server
- **WebSockets** - Real-time communication

### Frontend
- **React 18** - UI framework
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **Recharts** - Data visualization
- **React Router** - Navigation
- **Axios** - HTTP client
- **Lucide React** - Icons

### DevOps
- **Docker** - Containerization
- **Docker Compose** - Orchestration
- **Nginx** - Frontend server & reverse proxy

## 📁 Project Structure

```
ups-digital-twin/
├── backend/
│   ├── app/
│   │   ├── api/routes/          # API endpoints
│   │   ├── core/                # Configuration
│   │   ├── ml/                  # ML models and data generation
│   │   ├── models/              # Pydantic models
│   │   ├── services/            # Business logic
│   │   └── main.py              # FastAPI application
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/          # React components
│   │   ├── pages/               # Page components
│   │   ├── services/            # API client
│   │   ├── types/               # TypeScript types
│   │   ├── hooks/               # Custom hooks
│   │   └── utils/               # Helper functions
│   ├── Dockerfile
│   ├── nginx.conf
│   └── package.json
├── docker-compose.yml
└── README.md
```

## 🧪 Synthetic Data

The system generates realistic synthetic data for 12 UPS units with:

**Normal Operation** (70% of fleet):
- Stable voltage, normal temperatures
- Battery SOC 95-100%
- Load 30-75%

**Warning Conditions** (20% of fleet):
- Battery degradation patterns
- Elevated temperatures
- Input power fluctuations

**Critical Conditions** (10% of fleet):
- Imminent failure scenarios
- Severe anomalies
- Multiple risk factors

## 🔮 Future Enhancements

### SCADA Integration
- Replace synthetic data with real SCADA connections
- Support for OPC-UA, Modbus, MQTT protocols
- Historical data import from existing systems

### Advanced Analytics
- Predictive maintenance scheduling
- Cost-benefit analysis
- ROI calculations
- Custom report generation

### Deployment Options
- Cloud deployment (AWS, Azure, GCP)
- Edge computing support
- Multi-site federation
- High-availability configuration

### Additional Features
- User authentication and RBAC
- Email/SMS alert notifications
- Mobile app companion
- Custom dashboard builder
- Export to PDF/Excel

## 📝 License

This project is a demonstration/POC system. For production use, appropriate licensing should be established.

## 🤝 Support

For questions or issues:
1. Check the API documentation at `/docs`
2. Review the code comments and docstrings
3. Examine the example requests in the API

## 🎯 Project Goals

This system demonstrates:
✅ End-to-end ML pipeline (data → training → inference → deployment)
✅ Production-quality code architecture
✅ Real-time data streaming
✅ Interactive data visualization
✅ Scalable system design
✅ Comprehensive documentation
✅ Docker containerization
✅ RESTful API design
✅ Modern frontend development

Perfect for showcasing capabilities in:
- Digital Twin development
- Predictive maintenance
- Industrial IoT
- ML engineering
- Full-stack development
- System architecture
