import { useQuery } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { api } from '@/services/api'
import { CongestionLevel } from '@/types'
import CongestionCard from '@/components/CongestionCard'
import AlertsList from '@/components/AlertsList'
import { Car, AlertTriangle, Gauge, MapPin } from 'lucide-react'

export default function DashboardPage() {
  const navigate = useNavigate()

  const { data: overview, isLoading } = useQuery({
    queryKey: ['dashboard-overview'],
    queryFn: () => api.getDashboardOverview(),
    refetchInterval: 30000,
  })

  const { data: alerts = [] } = useQuery({
    queryKey: ['alerts'],
    queryFn: () => api.getAlerts(),
    refetchInterval: 30000,
  })

  const { data: roads = [] } = useQuery({
    queryKey: ['admin-roads-public'],
    queryFn: () => api.listRoads(true),
  })

  if (isLoading) {
    return (
      <div className="loading-page">
        <div className="spinner" />
        <span>Loading dashboard...</span>
      </div>
    )
  }

  const { congestion_stats, total_vehicles_detected, active_alerts, average_speed } = overview || {}

  return (
    <div>
      <div className="page-header">
        <h1>Overview</h1>
        <p>Real-time traffic monitoring across all road segments.</p>
      </div>

      {/* Stat Cards */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon blue"><MapPin size={20} /></div>
          <div className="stat-content">
            <div className="stat-label">Total Roads</div>
            <div className="stat-value">{congestion_stats?.total_roads ?? 0}</div>
            <div className="stat-sub">monitored segments</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon green"><Car size={20} /></div>
          <div className="stat-content">
            <div className="stat-label">Vehicles Detected</div>
            <div className="stat-value">{(total_vehicles_detected ?? 0).toLocaleString()}</div>
            <div className="stat-sub">total across all roads</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon orange"><AlertTriangle size={20} /></div>
          <div className="stat-content">
            <div className="stat-label">Active Alerts</div>
            <div className="stat-value">{active_alerts ?? 0}</div>
            <div className="stat-sub">require attention</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon purple"><Gauge size={20} /></div>
          <div className="stat-content">
            <div className="stat-label">Average Speed</div>
            <div className="stat-value">
              {average_speed ? `${average_speed.toFixed(0)}` : '—'}
            </div>
            <div className="stat-sub">{average_speed ? 'km/h across network' : 'no data yet'}</div>
          </div>
        </div>
      </div>

      {/* Congestion Breakdown */}
      <div className="section">
        <div className="section-header">
          <h2>Congestion Breakdown</h2>
          <span className="refresh-badge"><span className="refresh-dot" />Auto-refresh 30s</span>
        </div>
        <div className="congestion-grid">
          <CongestionCard level={CongestionLevel.FREE_FLOW} count={congestion_stats?.free_flow ?? 0} label="Free Flow" />
          <CongestionCard level={CongestionLevel.MODERATE}  count={congestion_stats?.moderate ?? 0}  label="Moderate" />
          <CongestionCard level={CongestionLevel.CONGESTED} count={congestion_stats?.congested ?? 0} label="Congested" />
          <CongestionCard level={CongestionLevel.SEVERE}    count={congestion_stats?.severe ?? 0}    label="Severe" />
        </div>
      </div>

      {/* Road List */}
      {roads.length > 0 && (
        <div className="section">
          <div className="section-header">
            <h2>Road Segments</h2>
          </div>
          <div className="table-wrapper">
            <table>
              <thead>
                <tr>
                  <th>Road Name</th>
                  <th>Code</th>
                  <th>Type</th>
                  <th>Status</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {roads.map((road: any) => (
                  <tr key={road.id}>
                    <td style={{ fontWeight: 500 }}>{road.name}</td>
                    <td className="td-muted">{road.road_code}</td>
                    <td className="td-muted">{road.road_type ?? 'N/A'}</td>
                    <td>
                      <span className={`badge ${road.is_active ? 'badge-success' : 'badge-gray'}`}>
                        {road.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </td>
                    <td>
                      <button
                        className="btn btn-ghost btn-sm"
                        onClick={() => navigate(`/road/${road.id}`)}
                      >
                        View →
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Active Alerts */}
      <div className="section">
        <div className="section-header">
          <h2>Active Alerts</h2>
          {alerts.length > 0 && (
            <span className="badge badge-danger">{alerts.length} active</span>
          )}
        </div>
        <AlertsList alerts={alerts} />
      </div>
    </div>
  )
}
