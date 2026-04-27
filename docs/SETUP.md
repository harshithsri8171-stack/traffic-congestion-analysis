# Traffic Congestion Analysis - Setup Guide

## Prerequisites

- Python 3.11+
- Node.js 20+
- PostgreSQL 16+ (or use Docker)
- Docker & Docker Compose (optional, but recommended)

## Quick Start with Docker

1. Clone the repository
2. Copy environment files:
   ```bash
   cp backend/.env.example backend/.env
   cp frontend/.env.example frontend/.env
   ```

3. Update the `.env` files with your configuration

4. Start all services:
   ```bash
   docker-compose up -d
   ```

5. Access the application:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/api/v1/docs

## Manual Setup

### Backend Setup

1. Navigate to backend directory:
   ```bash
   cd backend
   ```

2. Create virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up PostgreSQL database:
   ```sql
   CREATE DATABASE traffic_db;
   ```

5. Copy and configure environment:
   ```bash
   cp .env.example .env
   # Edit .env with your database credentials
   ```

6. Run database migrations:
   ```bash
   alembic upgrade head
   ```

7. Start the backend server:
   ```bash
   python -m app.main
   # Or with uvicorn directly:
   uvicorn app.main:app --reload
   ```

### Frontend Setup

1. Navigate to frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Copy and configure environment:
   ```bash
   cp .env.example .env
   ```

4. Start development server:
   ```bash
   npm run dev
   ```

## Configuration

### Backend Configuration (backend/.env)

```env
# Database
DATABASE_URL=postgresql://postgres:password@localhost:5432/traffic_db

# JWT
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30

# ML Model
MODEL_PATH=../data/models/yolov8n.pt
CONFIDENCE_THRESHOLD=0.5

# Video Processing
FRAME_SKIP=5
VIDEO_UPLOAD_PATH=../data/videos
```

### Frontend Configuration (frontend/.env)

```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_WS_URL=ws://localhost:8000/ws
```

## First Time Setup

### Create Admin User

After starting the backend, register a user through the API:

```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "email": "admin@example.com",
    "password": "adminpass123",
    "role": "admin"
  }'
```

### Add Sample Roads

Use the admin panel or API to add road segments:

```bash
curl -X POST "http://localhost:8000/api/v1/admin/add-road" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Main Street",
    "road_code": "MS001",
    "lanes": 4,
    "road_type": "arterial",
    "area_sqm": 2000
  }'
```

## Development

### Running Tests

Backend:
```bash
cd backend
pytest
```

Frontend:
```bash
cd frontend
npm run test
```

### Database Migrations

Create new migration:
```bash
cd backend
alembic revision --autogenerate -m "Description"
```

Apply migrations:
```bash
alembic upgrade head
```

Rollback:
```bash
alembic downgrade -1
```

## Troubleshooting

### Database Connection Issues

- Verify PostgreSQL is running
- Check database credentials in `.env`
- Ensure database exists: `CREATE DATABASE traffic_db;`

### Port Conflicts

- Backend (8000) or Frontend (3000) ports might be in use
- Change ports in docker-compose.yml or run commands

### YOLO Model Download

The YOLO model will be automatically downloaded on first use. For manual setup:

```bash
cd backend
python -c "from ultralytics import YOLO; YOLO('yolov8n.pt')"
```

## Next Steps

- Read [ARCHITECTURE.md](./ARCHITECTURE.md) for system design
- Check [API.md](./API.md) for API documentation
- Start processing traffic videos
- Configure alerts and thresholds
