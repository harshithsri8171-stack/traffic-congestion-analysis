# Traffic Congestion Analysis Dashboard

A real-time traffic congestion analysis system using AI and computer vision to monitor, analyze, and visualize traffic flow. The system provides accurate congestion detection, trend analysis, and actionable insights for smart city traffic management.

## Features

- **Real-Time Traffic Monitoring**: Live traffic data processing and visualization
- **AI-Powered Vehicle Detection**: YOLOv8-based vehicle detection and classification
- **Congestion Analysis**: Multi-factor congestion level classification (Free Flow, Moderate, Congested, Severe)
- **Interactive Dashboard**: Real-time charts, heatmaps, and analytics
- **Trend Analysis**: Historical data analysis with hourly, daily, and weekly trends
- **Peak Hour Analytics**: Identify recurring traffic patterns and bottlenecks
- **Alert System**: Automated alerts for traffic congestion events
- **Role-Based Access**: Admin, Authority, and Commuter user roles
- **RESTful API**: Comprehensive API for integration
- **WebSocket Support**: Real-time updates via WebSocket

## Technology Stack

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL 16
- **ORM**: SQLAlchemy
- **Authentication**: JWT (python-jose)
- **ML/CV**: YOLOv8, OpenCV, NumPy
- **API Documentation**: Swagger/OpenAPI

### Frontend
- **Framework**: React 18 + TypeScript
- **Build Tool**: Vite
- **Routing**: React Router
- **State Management**: Zustand
- **Data Fetching**: TanStack Query
- **Visualization**: Recharts
- **Maps**: React Leaflet

### Infrastructure
- **Containerization**: Docker & Docker Compose
- **Database Migrations**: Alembic

## Quick Start

### Using Docker (Recommended)

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd traffic-congestion-analysis
   ```

2. Set up environment files:
   ```bash
   cp backend/.env.example backend/.env
   cp frontend/.env.example frontend/.env
   ```

3. Start all services:
   ```bash
   docker-compose up -d
   ```

4. Access the application:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/api/v1/docs

### Manual Setup

See [SETUP.md](./docs/SETUP.md) for detailed installation instructions.

## Project Structure

```
traffic-congestion-analysis/
├── backend/                    # FastAPI Backend
│   ├── app/
│   │   ├── api/               # API endpoints
│   │   ├── models/            # Database models
│   │   ├── schemas/           # Pydantic schemas
│   │   ├── services/          # Business logic
│   │   ├── ml/                # ML/CV modules
│   │   └── utils/             # Utilities
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/                   # React Frontend
│   ├── src/
│   │   ├── components/        # UI components
│   │   ├── pages/             # Page components
│   │   ├── services/          # API client
│   │   ├── stores/            # State management
│   │   └── types/             # TypeScript types
│   ├── package.json
│   └── Dockerfile
│
├── docs/                       # Documentation
│   ├── SETUP.md               # Setup guide
│   ├── ARCHITECTURE.md        # System architecture
│   └── API.md                 # API documentation
│
├── data/                       # Data directory
│   ├── videos/                # Video uploads
│   ├── datasets/              # Training datasets
│   └── models/                # ML models
│
└── docker-compose.yml          # Docker Compose config
```

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register user
- `POST /api/v1/auth/login` - Login user
- `GET /api/v1/auth/profile` - Get profile
- `POST /api/v1/auth/logout` - Logout

### Dashboard
- `GET /api/v1/dashboard/overview` - Dashboard overview
- `GET /api/v1/dashboard/road/{road_id}` - Road-specific data
- `GET /api/v1/dashboard/trends` - Traffic trends
- `GET /api/v1/dashboard/heatmap` - Congestion heatmap
- `GET /api/v1/dashboard/alerts` - Active alerts
- `GET /api/v1/dashboard/peak-hours` - Peak hour analytics
- `GET /api/v1/dashboard/comparison` - Compare roads

### Traffic
- `POST /api/v1/traffic/upload-video` - Upload video
- `POST /api/v1/traffic/live-feed` - Register live feed
- `POST /api/v1/traffic/data` - Insert traffic data
- `GET /api/v1/traffic/live/{road_id}` - Live traffic data
- `GET /api/v1/traffic/history/{road_id}` - Traffic history

### Admin
- `POST /api/v1/admin/add-road` - Add road
- `PUT /api/v1/admin/update-road/{road_id}` - Update road
- `DELETE /api/v1/admin/delete-road/{road_id}` - Delete road
- `GET /api/v1/admin/roads` - List roads
- `GET /api/v1/admin/users` - List users

See [API.md](./docs/API.md) for complete API documentation.

## System Architecture

The system follows a microservices architecture with clear separation of concerns:

1. **Data Layer**: PostgreSQL database with optimized schema
2. **Processing Layer**: ML/CV pipeline for vehicle detection and analysis
3. **Backend Layer**: FastAPI REST APIs with JWT authentication
4. **Frontend Layer**: React dashboard with real-time updates
5. **WebSocket Layer**: Real-time traffic data streaming

See [ARCHITECTURE.md](./docs/ARCHITECTURE.md) for detailed architecture documentation.

## ML/CV Pipeline

1. **Video Preprocessing**: Frame extraction, denoising, contrast enhancement
2. **Vehicle Detection**: YOLOv8-based object detection
3. **Feature Extraction**: Density, speed, vehicle counts
4. **Classification**: Congestion level determination
5. **Storage**: Database persistence
6. **Visualization**: Dashboard rendering

## User Roles

- **Admin**: Full system access, user and road management
- **Authority**: Traffic monitoring, data upload, alerts management
- **Commuter**: View-only access to traffic data and trends

## Key Features Explained

### Congestion Classification
Traffic is classified into four levels based on density and speed:
- **Free Flow**: Low density, high speed
- **Moderate**: Medium density, normal speed
- **Congested**: High density, reduced speed
- **Severe**: Very high density, very low speed

### Trend Analysis
- Hourly trends (last 24 hours)
- Daily trends (last 7 days)
- Weekly trends (last 4 weeks)

### Alerts
Automated alerts triggered by:
- Congestion threshold breach
- Rapid traffic buildup
- Anomalous patterns

## Development

### Running Tests
```bash
# Backend
cd backend
pytest

# Frontend
cd frontend
npm run test
```

### Database Migrations
```bash
cd backend
alembic revision --autogenerate -m "Description"
alembic upgrade head
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License

## Support

For issues and questions:
- Open an issue on GitHub
- Check the documentation in `/docs`

## Future Enhancements

- [ ] Google Maps integration
- [ ] Mobile application
- [ ] Advanced tracking (DeepSORT)
- [ ] Predictive analytics
- [ ] Traffic signal optimization
- [ ] Route recommendation engine
- [ ] Multi-city support
- [ ] Cloud deployment

## Authors

- Your Name

## Acknowledgments

- YOLOv8 by Ultralytics
- FastAPI framework
- React community