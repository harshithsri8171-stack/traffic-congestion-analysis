# TrafficIQ — Traffic Congestion Analysis System

> Real-time traffic monitoring, congestion classification, and analytics dashboard powered by computer vision and machine learning.

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Tech Stack](#2-tech-stack)
3. [System Architecture](#3-system-architecture)
4. [Database Schema](#4-database-schema)
5. [API Reference](#5-api-reference)
6. [User Stories](#6-user-stories)
7. [Features](#7-features)
8. [ML Pipeline](#8-ml-pipeline)
9. [Setup Guide](#9-setup-guide)
10. [Environment Variables](#10-environment-variables)
11. [Project Structure](#11-project-structure)

---

## 1. Project Overview

**TrafficIQ** is a full-stack web application that enables city traffic authorities, analysts, and commuters to monitor and analyse road congestion in real time. It processes CCTV video footage through a YOLOv8-based vehicle detection pipeline, classifies congestion levels, stores historical records, and presents insights through an interactive dashboard.

### Goals
- Detect vehicle density and speed from CCTV/video feeds using deep learning.
- Classify roads into four congestion tiers: Free Flow, Moderate, Congested, Severe.
- Provide a real-time, role-based dashboard for traffic management.
- Expose a REST API for integration with third-party city systems.

---

## 2. Tech Stack

### Frontend
| Technology | Version | Purpose |
|---|---|---|
| React | 18 | UI framework |
| TypeScript | 5 | Type safety |
| Vite | 5 | Build tooling & dev server |
| React Router | 6 | Client-side routing |
| Zustand | 4 | Global authentication state |
| TanStack Query | 5 | Server-state caching & refetching |
| Axios | 1.6 | HTTP client |
| Recharts | 2 | Charts and trend graphs |
| React Leaflet + Leaflet | 4 / 1.9 | Interactive traffic heatmap |
| react-hot-toast | 2 | Toast notifications |
| lucide-react | 0.309 | Icon library |
| date-fns | 3 | Date formatting |

### Backend
| Technology | Version | Purpose |
|---|---|---|
| FastAPI | 0.109 | REST API framework |
| Uvicorn | 0.27 | ASGI server |
| SQLAlchemy | 2.0 | ORM |
| SQLite / PostgreSQL | — | Database (SQLite default for local dev) |
| Pydantic v2 | 2.5 | Request/response validation |
| pydantic-settings | 2.1 | Config from `.env` |
| python-jose | 3.3 | JWT token creation and validation |
| passlib + bcrypt | 1.7 | Password hashing |
| YOLOv8 (Ultralytics) | ≥8.1 | Vehicle detection model |
| OpenCV | ≥4.9 | Video frame processing |
| NumPy | ≥2.0 | Numerical computation |
| scikit-learn | ≥1.4 | ML utilities |
| PyTorch | ≥2.4 | Deep learning backend |
| Alembic | 1.13 | Database migrations |

### Infrastructure
| Technology | Purpose |
|---|---|
| Docker + Docker Compose | Containerised deployment |
| PostgreSQL 16 | Production database |
| WebSocket | Real-time traffic push (scaffolded) |

---

## 3. System Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                          Browser                               │
│  React 18 + TypeScript (Vite Dev Server :3000)                 │
│  ┌──────────────┐  ┌───────────┐  ┌────────┐  ┌──────────┐   │
│  │ Zustand Auth │  │TanStack Q │  │Recharts│  │React     │   │
│  │    Store     │  │ (caching) │  │ Charts │  │Leaflet   │   │
│  └──────────────┘  └───────────┘  └────────┘  └──────────┘   │
└──────────────────────────┬─────────────────────────────────────┘
                           │ HTTP / WebSocket
                           ▼
┌────────────────────────────────────────────────────────────────┐
│              FastAPI Application (:8000)                        │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  /api/v1/auth   /api/v1/traffic   /api/v1/dashboard      │  │
│  │  /api/v1/admin  /ws/traffic                              │  │
│  └────────────────┬─────────────────────────────────────────┘  │
│                   │                                             │
│  ┌────────────────▼─────────────────────────────────────────┐  │
│  │              ML Pipeline                                  │  │
│  │  VehicleDetector (YOLOv8) → FeatureExtraction            │  │
│  │  → CongestionClassifier  → TrafficRecord saved           │  │
│  └────────────────┬─────────────────────────────────────────┘  │
│                   │                                             │
│  ┌────────────────▼─────────────────────────────────────────┐  │
│  │  SQLAlchemy ORM → SQLite (dev) / PostgreSQL (prod)       │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────┘
```

### Data Flow — Video Analysis
```
Upload video (Admin/Authority)
    → POST /traffic/upload-video
    → VehicleDetector.process_video()   ← YOLOv8 per frame
    → Aggregate vehicle counts + density
    → CongestionClassifier.classify()   ← density + speed weighted
    → TrafficRecord saved to DB
    → WebSocket broadcast to all clients
    → Dashboard re-fetches on 30s interval
```

### Authentication Flow
```
POST /auth/login  →  validate credentials
    →  create JWT (HS256, 30 min)
    →  frontend stores in localStorage
    →  all requests include: Authorization: Bearer <token>
    →  backend validates via get_current_user() dependency
    →  401 → auto-logout + redirect to /login
```

---

## 4. Database Schema

### `users`
| Column | Type | Notes |
|---|---|---|
| id | INTEGER PK | Auto-increment |
| email | VARCHAR(255) | Unique, indexed |
| username | VARCHAR(100) | Unique, indexed |
| hashed_password | VARCHAR(255) | bcrypt hash |
| full_name | VARCHAR(255) | Optional |
| role | ENUM | admin, authority, commuter |
| is_active | BOOLEAN | Default true |
| is_verified | BOOLEAN | Default false |
| created_at | DATETIME | Auto |
| updated_at | DATETIME | Auto on update |

### `roads`
| Column | Type | Notes |
|---|---|---|
| id | INTEGER PK | Auto-increment |
| name | VARCHAR(255) | Road display name |
| road_code | VARCHAR(50) | Unique identifier |
| start_point | VARCHAR(255) | Optional |
| end_point | VARCHAR(255) | Optional |
| latitude | FLOAT | For map display |
| longitude | FLOAT | For map display |
| length_km | FLOAT | Segment length |
| lanes | INTEGER | Default 2 |
| road_type | VARCHAR(50) | highway/arterial/local/etc. |
| area_sqm | FLOAT | For density calc |
| is_active | BOOLEAN | Default true |
| description | TEXT | Optional |

### `traffic_records`
| Column | Type | Notes |
|---|---|---|
| id | INTEGER PK | |
| road_id | INTEGER FK | → roads.id (CASCADE) |
| vehicle_count | INTEGER | Total |
| car_count | INTEGER | |
| truck_count | INTEGER | |
| bus_count | INTEGER | |
| motorcycle_count | INTEGER | |
| density | FLOAT | Vehicles/unit area |
| average_speed | FLOAT | km/h |
| congestion_level | ENUM | free_flow/moderate/congested/severe |
| congestion_score | FLOAT | 0–100 |
| timestamp | DATETIME | Indexed |
| hour_of_day | INTEGER | 0–23 |
| day_of_week | INTEGER | 0=Mon, 6=Sun |
| source | VARCHAR(50) | video/live_feed/api/seed |
| model_version | VARCHAR(50) | YOLOv8 version |
| confidence | FLOAT | Avg detection confidence |
| extra_data | JSON | Flexible metadata |

### `alerts`
| Column | Type | Notes |
|---|---|---|
| id | INTEGER PK | |
| road_id | INTEGER FK | → roads.id (CASCADE) |
| alert_type | ENUM | congestion/accident/slow_traffic/high_density |
| severity | ENUM | info/warning/critical |
| title | VARCHAR(255) | |
| message | TEXT | Optional |
| is_active | BOOLEAN | Default true |
| is_resolved | BOOLEAN | Default false |
| created_at | DATETIME | Indexed |
| resolved_at | DATETIME | When resolved |

---

## 5. API Reference

Base URL: `http://localhost:8000/api/v1`

### Authentication

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/auth/register` | None | Create new user account |
| POST | `/auth/login` | None | Login, returns JWT token |
| GET | `/auth/profile` | Bearer | Get current user profile |
| POST | `/auth/logout` | Bearer | Logout |

### Dashboard

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/dashboard/overview` | Bearer | Aggregated stats: congestion breakdown, vehicle count, alerts, avg speed |
| GET | `/dashboard/road/{road_id}` | Bearer | Per-road traffic summary |
| GET | `/dashboard/trends` | Bearer | Hourly/daily trends. Params: `road_id`, `period` |
| GET | `/dashboard/heatmap` | Bearer | All roads with lat/lng and congestion level |
| GET | `/dashboard/alerts` | Bearer | Active alerts list |
| GET | `/dashboard/peak-hours` | Bearer | Peak hour analytics |
| GET | `/dashboard/comparison` | Bearer | Compare two roads. Params: `road1_id`, `road2_id`, `hours` |

### Traffic

| Method | Endpoint | Auth | Role | Description |
|---|---|---|---|---|
| POST | `/traffic/upload-video` | Bearer | Admin/Authority | Upload CCTV video for ML processing |
| POST | `/traffic/live-feed` | Bearer | Admin/Authority | Register a live camera feed |
| GET | `/traffic/live/{road_id}` | Bearer | Any | Get latest real-time data |
| GET | `/traffic/history/{road_id}` | Bearer | Any | Historical records (limit param) |

### Admin

| Method | Endpoint | Auth | Role | Description |
|---|---|---|---|---|
| POST | `/admin/add-road` | Bearer | Admin | Add new road segment |
| PUT | `/admin/update-road/{id}` | Bearer | Admin | Update road details |
| DELETE | `/admin/delete-road/{id}` | Bearer | Admin | Delete road + all records |
| GET | `/admin/roads` | Bearer | Admin/Authority | List roads (`active_only` param) |
| GET | `/admin/users` | Bearer | Admin | List all users |
| PUT | `/admin/users/{id}/toggle-active` | Bearer | Admin | Toggle user active status |
| POST | `/admin/seed` | Bearer | Admin | Seed demo roads and traffic data |

### WebSocket

| Endpoint | Description |
|---|---|
| `ws://localhost:8000/ws/traffic` | Real-time congestion updates broadcast |

---

## 6. User Stories

### Commuter
- As a commuter, I want to see current congestion levels for all roads so I can plan my route.
- As a commuter, I want to view a colour-coded heatmap so I can visually identify bottlenecks.
- As a commuter, I want to see active alerts (accidents, severe congestion) so I can avoid affected roads.
- As a commuter, I want the dashboard to refresh automatically so I always see fresh data.

### Traffic Authority
- As a traffic authority, I want to upload CCTV video footage so the system can detect vehicle density automatically.
- As a traffic authority, I want to view 24-hour trend charts per road so I can identify peak hours.
- As a traffic authority, I want to compare two roads side-by-side so I can allocate traffic management resources.
- As a traffic authority, I want to see peak hour analytics so I can adjust signal timings.

### Administrator
- As an admin, I want to add, edit, and delete road segments so the monitored network stays up to date.
- As an admin, I want to manage user accounts and activate/deactivate users so access is controlled.
- As an admin, I want to seed demo data so stakeholders can evaluate the system quickly.
- As an admin, I want to assign roles (admin, authority, commuter) to control feature access.

---

## 7. Features

### Implemented
- **Role-based auth** — JWT login/register with three roles (Admin, Authority, Commuter)
- **Dashboard** — Live stat cards (roads, vehicles, alerts, avg speed) + congestion breakdown
- **Road list** — Table of all monitored roads with status, clickable to detail view
- **Road detail** — Per-road stat cards + 24-hour trend chart (vehicles + speed)
- **Traffic heatmap** — Interactive Leaflet map with colour-coded CircleMarkers per road
- **Active alerts** — Real-time alert list with severity badges
- **Admin: Road CRUD** — Add, edit, delete roads via modal forms with validation
- **Admin: User management** — View all users, activate/deactivate accounts
- **Admin: Seed data** — One-click demo data population (6 roads × 24h records)
- **Toast notifications** — Success/error feedback on all mutations
- **Auto-refresh** — Dashboard and heatmap auto-refetch at 30s / 60s intervals

### In Progress / Scaffolded
- **Video upload** — Backend route exists; ML pipeline is stubbed, needs model file
- **WebSocket real-time push** — Connection manager implemented; broadcast integration pending
- **Alembic migrations** — Schema management setup present

---

## 8. ML Pipeline

### Vehicle Detection — `VehicleDetector`
- Uses **YOLOv8 nano** (`yolov8n.pt`) pretrained on COCO
- Detects: `car`, `motorcycle`, `bus`, `truck`
- Per-frame inference with configurable confidence threshold (default 0.5) and NMS (0.4)
- Returns bounding boxes, class names, and confidence scores
- `process_video()` iterates frames with configurable skip interval (default every 5th frame)

### Congestion Classification — `CongestionClassifier`
- Inputs: vehicle density (vehicles/m²) and average speed (km/h)
- Weighted score: **60% speed contribution + 40% density contribution**
- Thresholds:

| Level | Speed | Density |
|---|---|---|
| Free Flow | > 50 km/h | < 0.01 veh/m² |
| Moderate | 30–50 km/h | 0.01–0.025 veh/m² |
| Congested | 15–30 km/h | 0.025–0.04 veh/m² |
| Severe | < 15 km/h | > 0.04 veh/m² |

- Returns congestion level enum + score (0–100) + recommendation text

---

## 9. Setup Guide

### Prerequisites
- Python 3.13+
- Node.js 18+
- (Optional) Docker Desktop for containerised PostgreSQL

### Local Development

#### Backend
```bash
cd backend

# Install dependencies
pip install -r requirements.txt
pip install "pydantic[email]"
pip install "python-jose[cryptography]"

# Create .env file
# (already created at backend/.env — uses SQLite by default)

# Start server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### Frontend
```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

Visit `http://localhost:3000`

### Docker (Full Stack)
```bash
docker-compose up
```
Services start in order: PostgreSQL → Backend → Frontend

---

## 10. Environment Variables

### Backend (`backend/.env`)
```env
DATABASE_URL=sqlite:///./traffic.db        # or postgresql://...
SECRET_KEY=your-secret-key-change-in-prod
DEBUG=True
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
ALLOWED_ORIGINS=http://localhost:3000
MODEL_PATH=../data/models/yolov8n.pt
CONFIDENCE_THRESHOLD=0.5
NMS_THRESHOLD=0.4
DENSITY_LOW=10
DENSITY_MEDIUM=25
DENSITY_HIGH=40
SPEED_THRESHOLD_FREE=50.0
SPEED_THRESHOLD_MODERATE=30.0
FRAME_SKIP=5
VIDEO_UPLOAD_PATH=../data/videos
MAX_UPLOAD_SIZE_MB=100
```

### Frontend (`frontend/.env`)
```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_WS_URL=ws://localhost:8000/ws
```

---

## 11. Project Structure

```
traffic-congestion-analysis/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── auth.py          # Auth routes
│   │   │   ├── traffic.py       # Traffic data routes
│   │   │   ├── dashboard.py     # Analytics routes
│   │   │   ├── admin.py         # Admin CRUD + seed
│   │   │   └── websocket.py     # WebSocket handler
│   │   ├── models/
│   │   │   ├── user.py
│   │   │   ├── road.py
│   │   │   ├── traffic_record.py
│   │   │   └── alert.py
│   │   ├── schemas/
│   │   │   ├── user.py
│   │   │   ├── road.py
│   │   │   ├── traffic.py
│   │   │   ├── dashboard.py
│   │   │   └── alert.py
│   │   ├── ml/
│   │   │   ├── vehicle_detection.py  # YOLOv8 detection
│   │   │   ├── classification.py     # Congestion classifier
│   │   │   ├── feature_extraction.py
│   │   │   └── preprocessing.py
│   │   ├── utils/
│   │   │   ├── security.py      # JWT + bcrypt
│   │   │   └── dependencies.py  # FastAPI deps
│   │   ├── main.py              # App entry point
│   │   ├── database.py          # SQLAlchemy engine
│   │   └── config.py            # Pydantic settings
│   ├── requirements.txt
│   ├── .env
│   └── Dockerfile
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Layout.tsx        # Sidebar + topbar
│   │   │   ├── Modal.tsx         # Reusable modal
│   │   │   ├── CongestionCard.tsx
│   │   │   └── AlertsList.tsx
│   │   ├── pages/
│   │   │   ├── LoginPage.tsx
│   │   │   ├── RegisterPage.tsx
│   │   │   ├── DashboardPage.tsx
│   │   │   ├── HeatmapPage.tsx
│   │   │   ├── RoadDetailPage.tsx
│   │   │   └── AdminPage.tsx
│   │   ├── services/
│   │   │   └── api.ts            # Axios service
│   │   ├── stores/
│   │   │   └── authStore.ts      # Zustand auth
│   │   ├── types/
│   │   │   └── index.ts
│   │   ├── styles/
│   │   │   └── index.css         # Design system
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   ├── vite.config.ts
│   └── Dockerfile
│
├── data/
│   ├── videos/                   # Uploaded CCTV footage
│   ├── datasets/                 # Training data
│   └── models/                   # yolov8n.pt
│
├── docs/
├── docker-compose.yml
├── DOCUMENTATION.md              # ← This file
└── README.md
```

---

*Generated for TrafficIQ v1.0 — 2026*
