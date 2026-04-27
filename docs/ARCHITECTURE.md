# System Architecture

## Overview

The Traffic Congestion Analysis Dashboard is built using a modern microservices architecture with the following components:

```
┌─────────────────┐
│   Frontend      │ (React + TypeScript)
│   (Port 3000)   │
└────────┬────────┘
         │ HTTP/WebSocket
         │
┌────────▼────────┐
│   Backend       │ (FastAPI + Python)
│   (Port 8000)   │
└────────┬────────┘
         │
    ┌────▼─────┬─────────┐
    │          │         │
┌───▼──┐  ┌───▼───┐ ┌──▼────┐
│ DB   │  │  ML   │ │ Video │
│ PG   │  │ YOLO  │ │ Data  │
└──────┘  └───────┘ └───────┘
```

## Components

### 1. Frontend (React + TypeScript)

**Technology Stack:**
- React 18
- TypeScript
- Vite (Build tool)
- React Router (Routing)
- TanStack Query (Data fetching)
- Recharts (Visualization)
- Zustand (State management)

**Key Features:**
- Real-time dashboard with traffic statistics
- Road-specific detailed views
- Traffic heatmap visualization
- Admin panel for road/user management
- JWT-based authentication
- WebSocket support for live updates

**Directory Structure:**
```
frontend/src/
├── components/     # Reusable UI components
├── pages/          # Page components
├── services/       # API client
├── stores/         # State management
├── types/          # TypeScript definitions
└── styles/         # CSS styles
```

### 2. Backend (FastAPI)

**Technology Stack:**
- FastAPI (Web framework)
- SQLAlchemy (ORM)
- PostgreSQL (Database)
- Alembic (Migrations)
- Python-JOSE (JWT)
- Pydantic (Validation)

**Key Features:**
- RESTful API endpoints
- JWT authentication & authorization
- Role-based access control (Admin, Authority, Commuter)
- WebSocket for real-time updates
- Video upload and processing
- Traffic data aggregation

**Directory Structure:**
```
backend/app/
├── api/            # API route handlers
├── models/         # Database models
├── schemas/        # Pydantic schemas
├── services/       # Business logic
├── ml/             # ML & CV modules
├── utils/          # Utilities
├── config.py       # Configuration
└── main.py         # Application entry
```

### 3. Database (PostgreSQL)

**Schema:**

**Users Table:**
- id, email, username, hashed_password
- role (admin, authority, commuter)
- is_active, is_verified
- created_at, updated_at

**Roads Table:**
- id, name, road_code
- location details (lat/lng, start/end points)
- characteristics (length, lanes, area)
- is_active, description

**Traffic Records Table:**
- id, road_id, timestamp
- vehicle counts (total, car, truck, bus, motorcycle)
- metrics (density, avg_speed)
- congestion_level, congestion_score
- source, model_version, confidence

**Alerts Table:**
- id, road_id, alert_type, severity
- title, message
- is_active, is_resolved
- created_at, resolved_at

### 4. ML/CV Pipeline

**Components:**

1. **Video Preprocessing** (`preprocessing.py`)
   - Frame extraction
   - Noise reduction
   - Contrast enhancement
   - Resizing and normalization

2. **Vehicle Detection** (`vehicle_detection.py`)
   - YOLOv8 model for object detection
   - Vehicle classification (car, truck, bus, motorcycle)
   - Bounding box extraction
   - Confidence scoring

3. **Feature Extraction** (`feature_extraction.py`)
   - Traffic density calculation
   - Speed estimation (simplified)
   - Vehicle counting by type
   - Congestion score computation

4. **Classification** (`classification.py`)
   - Congestion level determination
   - Multi-factor classification (density + speed)
   - Threshold-based categorization
   - Recommendation generation

**Processing Flow:**
```
Video Input
    ↓
Preprocessing (resize, denoise, enhance)
    ↓
Vehicle Detection (YOLO)
    ↓
Feature Extraction (density, speed, counts)
    ↓
Classification (free/moderate/congested/severe)
    ↓
Database Storage
    ↓
Dashboard Display
```

## API Architecture

### Authentication Flow

1. User submits credentials to `/api/v1/auth/login`
2. Backend validates credentials
3. JWT token generated and returned
4. Client stores token in localStorage
5. Token included in subsequent requests (Authorization header)
6. Backend validates token and extracts user info

### Data Flow

**Traffic Data Ingestion:**
```
Video Upload
    ↓
POST /api/v1/traffic/upload-video
    ↓
Background Processing (ML Pipeline)
    ↓
POST /api/v1/traffic/data (save results)
    ↓
WebSocket Broadcast
    ↓
Frontend Updates
```

**Dashboard Updates:**
```
Frontend Component Mount
    ↓
GET /api/v1/dashboard/overview
    ↓
Query Latest Traffic Records
    ↓
Aggregate Statistics
    ↓
Return JSON Response
    ↓
Frontend Renders Charts
    ↓
Auto-refresh every 30s
```

## Real-Time Updates

**WebSocket Connection:**
```
Client connects to ws://localhost:8000/ws/traffic
    ↓
Server accepts connection
    ↓
Client added to active connections list
    ↓
When new traffic data processed:
    ↓
Server broadcasts to all connected clients
    ↓
Clients update UI in real-time
```

## Security

1. **Authentication:**
   - JWT tokens with expiration
   - Secure password hashing (bcrypt)
   - Token refresh mechanism

2. **Authorization:**
   - Role-based access control
   - Protected endpoints
   - Admin-only operations

3. **Data Validation:**
   - Pydantic schemas for input validation
   - SQL injection prevention (SQLAlchemy ORM)
   - CORS configuration

## Scalability Considerations

1. **Database:**
   - Indexed columns (road_id, timestamp, congestion_level)
   - Partitioning by date for large datasets
   - Regular cleanup of old records

2. **Processing:**
   - Async video processing
   - Queue-based architecture (future: Celery + Redis)
   - GPU acceleration for ML inference

3. **Caching:**
   - Dashboard data caching (future: Redis)
   - API response caching
   - Static asset CDN

## Deployment

**Development:**
- Docker Compose for local development
- Hot reload enabled for both frontend/backend

**Production:**
- Kubernetes orchestration
- Load balancing (Nginx)
- Database replication
- CDN for static assets
- Monitoring (Prometheus + Grafana)

## Future Enhancements

1. Google Maps API integration
2. Mobile application
3. Advanced ML models (DeepSORT tracking)
4. Real-time camera feeds
5. Predictive analytics
6. Multi-city support
7. Traffic signal optimization
8. Route recommendation engine
