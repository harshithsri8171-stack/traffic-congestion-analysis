# API Documentation

Base URL: `http://localhost:8000/api/v1`

## Authentication

### Register User

**POST** `/auth/register`

Register a new user account.

**Request Body:**
```json
{
  "username": "johndoe",
  "email": "john@example.com",
  "password": "securepass123",
  "full_name": "John Doe",
  "role": "commuter"
}
```

**Response:** `201 Created`
```json
{
  "id": 1,
  "username": "johndoe",
  "email": "john@example.com",
  "full_name": "John Doe",
  "role": "commuter",
  "is_active": true,
  "is_verified": false,
  "created_at": "2026-02-15T10:00:00Z"
}
```

### Login

**POST** `/auth/login`

Login and receive JWT token.

**Request Body:** (form-urlencoded)
```
username=johndoe
password=securepass123
```

**Response:** `200 OK`
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Get Profile

**GET** `/auth/profile`

Get current user profile.

**Headers:**
```
Authorization: Bearer <token>
```

**Response:** `200 OK`
```json
{
  "id": 1,
  "username": "johndoe",
  "email": "john@example.com",
  "role": "commuter",
  "is_active": true
}
```

### Logout

**POST** `/auth/logout`

Logout user (client should discard token).

**Headers:**
```
Authorization: Bearer <token>
```

**Response:** `200 OK`
```json
{
  "message": "Successfully logged out"
}
```

---

## Dashboard

### Get Dashboard Overview

**GET** `/dashboard/overview`

Get overall congestion summary.

**Response:** `200 OK`
```json
{
  "congestion_stats": {
    "total_roads": 25,
    "free_flow": 10,
    "moderate": 8,
    "congested": 5,
    "severe": 2
  },
  "total_vehicles_detected": 1250,
  "active_alerts": 3,
  "last_updated": "2026-02-15T10:30:00Z",
  "average_speed": 45.5
}
```

### Get Road Data

**GET** `/dashboard/road/{road_id}`

Get road-specific traffic data.

**Response:** `200 OK`
```json
{
  "road_id": 1,
  "road_name": "Main Street",
  "road_code": "MS001",
  "current_congestion": "moderate",
  "vehicle_count": 45,
  "average_speed": 35.2,
  "density": 0.0225,
  "last_updated": "2026-02-15T10:30:00Z",
  "congestion_score": 42.5
}
```

### Get Trends

**GET** `/dashboard/trends?road_id={road_id}&period={period}`

Get traffic trends.

**Query Parameters:**
- `road_id` (required): Road ID
- `period` (optional): "hourly", "daily", or "weekly" (default: "hourly")

**Response:** `200 OK`
```json
{
  "road_id": 1,
  "road_name": "Main Street",
  "period": "hourly",
  "data_points": [
    {
      "timestamp": "2026-02-15T09:00:00Z",
      "vehicle_count": 32,
      "congestion_level": "free_flow",
      "average_speed": 55.0
    },
    {
      "timestamp": "2026-02-15T10:00:00Z",
      "vehicle_count": 45,
      "congestion_level": "moderate",
      "average_speed": 35.2
    }
  ]
}
```

### Get Heatmap

**GET** `/dashboard/heatmap`

Get congestion heatmap data.

**Response:** `200 OK`
```json
{
  "timestamp": "2026-02-15T10:30:00Z",
  "points": [
    {
      "road_id": 1,
      "road_name": "Main Street",
      "road_code": "MS001",
      "latitude": 40.7128,
      "longitude": -74.0060,
      "congestion_score": 42.5,
      "congestion_level": "moderate"
    }
  ]
}
```

### Get Active Alerts

**GET** `/dashboard/alerts`

Get active congestion alerts.

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "road_id": 5,
    "alert_type": "congestion",
    "severity": "critical",
    "title": "Severe Congestion on Highway 101",
    "message": "Major delays expected",
    "created_at": "2026-02-15T10:15:00Z"
  }
]
```

### Get Peak Hours

**GET** `/dashboard/peak-hours?road_id={road_id}`

Get peak hour analytics.

**Query Parameters:**
- `road_id` (optional): Specific road ID (omit for all roads)

**Response:** `200 OK`
```json
{
  "road_id": null,
  "peak_hours": [
    {
      "hour": 8,
      "day_of_week": 1,
      "average_vehicle_count": 78.5,
      "average_congestion_score": 65.2,
      "most_common_level": "congested"
    }
  ]
}
```

### Compare Roads

**GET** `/dashboard/comparison?road1_id={id1}&road2_id={id2}&hours={hours}`

Compare two road segments.

**Query Parameters:**
- `road1_id` (required): First road ID
- `road2_id` (required): Second road ID
- `hours` (optional): Time period in hours (default: 24)

**Response:** `200 OK`
```json
{
  "road1_id": 1,
  "road1_name": "Main Street",
  "road1_avg_congestion": 42.5,
  "road1_avg_vehicles": 45.0,
  "road2_id": 2,
  "road2_name": "Second Avenue",
  "road2_avg_congestion": 58.3,
  "road2_avg_vehicles": 62.0,
  "time_period": "Last 24 hours"
}
```

---

## Traffic

### Upload Video

**POST** `/traffic/upload-video`

Upload CCTV footage for processing (Admin/Authority only).

**Headers:**
```
Authorization: Bearer <token>
Content-Type: multipart/form-data
```

**Form Data:**
- `file`: Video file
- `road_id`: Road ID (optional)

**Response:** `202 Accepted`
```json
{
  "message": "Video upload accepted for processing",
  "filename": "traffic_video.mp4",
  "road_id": 1,
  "status": "processing"
}
```

### Register Live Feed

**POST** `/traffic/live-feed`

Register a live feed for continuous monitoring (Admin/Authority only).

**Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "road_id": 1,
  "live_feed_url": "rtsp://camera.example.com/stream",
  "process_immediately": true
}
```

**Response:** `201 Created`
```json
{
  "message": "Live feed registered successfully",
  "road_id": 1,
  "status": "active"
}
```

### Insert Traffic Data

**POST** `/traffic/data`

Insert processed traffic metrics.

**Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "road_id": 1,
  "vehicle_count": 45,
  "car_count": 35,
  "truck_count": 5,
  "bus_count": 3,
  "motorcycle_count": 2,
  "density": 0.0225,
  "average_speed": 35.2,
  "congestion_level": "moderate",
  "congestion_score": 42.5,
  "source": "video",
  "model_version": "yolov8n",
  "confidence": 0.85
}
```

**Response:** `201 Created`
```json
{
  "id": 123,
  "road_id": 1,
  "vehicle_count": 45,
  "congestion_level": "moderate",
  "timestamp": "2026-02-15T10:30:00Z"
}
```

### Get Live Traffic

**GET** `/traffic/live/{road_id}`

Get real-time traffic data for a specific road.

**Response:** `200 OK`
```json
{
  "id": 123,
  "road_id": 1,
  "vehicle_count": 45,
  "average_speed": 35.2,
  "congestion_level": "moderate",
  "timestamp": "2026-02-15T10:30:00Z"
}
```

### Get Traffic History

**GET** `/traffic/history/{road_id}?limit={limit}`

Get historical traffic data for a road.

**Query Parameters:**
- `limit` (optional): Number of records (default: 100)

**Response:** `200 OK`
```json
[
  {
    "id": 123,
    "road_id": 1,
    "vehicle_count": 45,
    "congestion_level": "moderate",
    "timestamp": "2026-02-15T10:30:00Z"
  }
]
```

---

## Admin

All admin endpoints require `admin` role.

### Add Road

**POST** `/admin/add-road`

Add a new road segment.

**Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "name": "Main Street",
  "road_code": "MS001",
  "start_point": "Downtown",
  "end_point": "Suburb",
  "latitude": 40.7128,
  "longitude": -74.0060,
  "length_km": 5.2,
  "lanes": 4,
  "road_type": "arterial",
  "area_sqm": 2000,
  "description": "Main arterial road"
}
```

**Response:** `201 Created`

### Update Road

**PUT** `/admin/update-road/{road_id}`

Update road segment.

**Response:** `200 OK`

### Delete Road

**DELETE** `/admin/delete-road/{road_id}`

Delete road segment.

**Response:** `204 No Content`

### List Roads

**GET** `/admin/roads?active_only={bool}&skip={int}&limit={int}`

List all roads (Admin/Authority).

**Response:** `200 OK`

### List Users

**GET** `/admin/users?skip={int}&limit={int}`

List all users (Admin only).

**Response:** `200 OK`

### Toggle User Active

**PUT** `/admin/users/{user_id}/toggle-active`

Toggle user active status.

**Response:** `200 OK`

---

## WebSocket

### Traffic Updates

**WS** `/ws/traffic`

WebSocket connection for live traffic updates.

**Connection:**
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/traffic');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log(data);
};
```

**Message Types:**
- `connection`: Initial connection confirmation
- `ping`: Keep-alive message
- `traffic_update`: New traffic data available

---

## Error Responses

All endpoints may return the following error responses:

**400 Bad Request**
```json
{
  "detail": "Invalid input data"
}
```

**401 Unauthorized**
```json
{
  "detail": "Could not validate credentials"
}
```

**403 Forbidden**
```json
{
  "detail": "Access denied. Required roles: ['admin']"
}
```

**404 Not Found**
```json
{
  "detail": "Resource not found"
}
```

**500 Internal Server Error**
```json
{
  "detail": "Internal server error"
}
```
