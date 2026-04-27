export enum CongestionLevel {
  FREE_FLOW = 'free_flow',
  MODERATE = 'moderate',
  CONGESTED = 'congested',
  SEVERE = 'severe',
}

export enum UserRole {
  ADMIN = 'admin',
  AUTHORITY = 'authority',
  COMMUTER = 'commuter',
}

export interface User {
  id: number
  email: string
  username: string
  full_name?: string
  role: UserRole
  is_active: boolean
  is_verified: boolean
  created_at: string
}

export interface Road {
  id: number
  name: string
  road_code: string
  start_point?: string
  end_point?: string
  latitude?: number
  longitude?: number
  length_km?: number
  lanes: number
  road_type?: string
  area_sqm?: number
  is_active: boolean
  description?: string
  created_at: string
}

export interface TrafficRecord {
  id: number
  road_id: number
  vehicle_count: number
  car_count: number
  truck_count: number
  bus_count: number
  motorcycle_count: number
  density?: number
  average_speed?: number
  congestion_level: CongestionLevel
  congestion_score?: number
  timestamp: string
  hour_of_day?: number
  day_of_week?: number
  source?: string
  model_version?: string
  confidence?: number
}

export interface CongestionStats {
  total_roads: number
  free_flow: number
  moderate: number
  congested: number
  severe: number
}

export interface DashboardOverview {
  congestion_stats: CongestionStats
  total_vehicles_detected: number
  active_alerts: number
  last_updated: string
  average_speed?: number
}

export interface RoadTrafficData {
  road_id: number
  road_name: string
  road_code: string
  current_congestion: CongestionLevel
  vehicle_count: number
  average_speed?: number
  density?: number
  last_updated: string
  congestion_score?: number
}

export interface TrendDataPoint {
  timestamp: string
  vehicle_count: number
  congestion_level: CongestionLevel
  average_speed?: number
}

export interface TrendData {
  road_id: number
  road_name: string
  period: string
  data_points: TrendDataPoint[]
}

export interface HeatmapPoint {
  road_id: number
  road_name: string
  road_code: string
  latitude?: number
  longitude?: number
  congestion_score: number
  congestion_level: CongestionLevel
}

export interface Alert {
  id: number
  road_id: number
  alert_type: string
  severity: string
  title: string
  message?: string
  is_active: boolean
  is_resolved: boolean
  created_at: string
}
