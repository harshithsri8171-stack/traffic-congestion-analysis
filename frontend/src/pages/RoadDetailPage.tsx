import { useParams, useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { api } from '@/services/api'
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid,
  Tooltip, Legend, ResponsiveContainer,
} from 'recharts'
import { format } from 'date-fns'
import { ArrowLeft, Car, Gauge, Activity, TrendingUp } from 'lucide-react'

const LEVEL_CONFIG: Record<string, { badge: string; label: string }> = {
  free_flow: { badge: 'badge-success', label: 'Free Flow' },
  moderate:  { badge: 'badge-warning', label: 'Moderate'  },
  congested: { badge: 'badge-orange',  label: 'Congested' },
  severe:    { badge: 'badge-danger',  label: 'Severe'    },
}

export default function RoadDetailPage() {
  const { roadId } = useParams<{ roadId: string }>()
  const navigate   = useNavigate()

  const { data: roadData, isLoading } = useQuery({
    queryKey: ['road-data', roadId],
    queryFn: () => api.getRoadData(Number(roadId)),
    enabled: !!roadId,
  })

  const { data: trends } = useQuery({
    queryKey: ['trends', roadId],
    queryFn: () => api.getTrends(Number(roadId), 'hourly'),
    enabled: !!roadId,
  })

  if (isLoading) {
    return (
      <div className="loading-page">
        <div className="spinner" />
        <span>Loading road data...</span>
      </div>
    )
  }

  if (!roadData) {
    return (
      <div className="empty-state" style={{ marginTop: '4rem' }}>
        <h3>Road not found</h3>
        <p>The road you're looking for doesn't exist or has no data yet.</p>
        <button className="btn btn-primary" style={{ marginTop: '1rem' }} onClick={() => navigate('/')}>
          Back to Dashboard
        </button>
      </div>
    )
  }

  const level    = roadData.current_congestion ?? 'free_flow'
  const lvlCfg   = LEVEL_CONFIG[level] ?? LEVEL_CONFIG.free_flow

  const chartData = (trends?.data_points ?? []).map((p: any) => ({
    time: format(new Date(p.timestamp), 'HH:mm'),
    vehicles: p.vehicle_count,
    speed: p.average_speed ?? 0,
  }))

  return (
    <div>
      {/* Header */}
      <div style={{ marginBottom: '1.75rem' }}>
        <button className="back-btn" onClick={() => navigate('/')}>
          <ArrowLeft size={15} /> Back to Dashboard
        </button>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.875rem', marginTop: '0.75rem' }}>
          <h1 style={{ fontSize: '1.5rem', fontWeight: 700, letterSpacing: '-0.02em' }}>
            {roadData.road_name}
          </h1>
          <span className="badge badge-gray">{roadData.road_code}</span>
          <span className={`badge ${lvlCfg.badge}`}>{lvlCfg.label}</span>
        </div>
      </div>

      {/* Stats */}
      <div className="stats-grid" style={{ marginBottom: '1.75rem' }}>
        <div className="stat-card">
          <div className="stat-icon blue"><Activity size={20} /></div>
          <div className="stat-content">
            <div className="stat-label">Current Status</div>
            <div className="stat-value" style={{ fontSize: '1.25rem' }}>{lvlCfg.label}</div>
            <div className="stat-sub">congestion level</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon green"><Car size={20} /></div>
          <div className="stat-content">
            <div className="stat-label">Vehicle Count</div>
            <div className="stat-value">{roadData.vehicle_count ?? 0}</div>
            <div className="stat-sub">vehicles detected</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon purple"><Gauge size={20} /></div>
          <div className="stat-content">
            <div className="stat-label">Average Speed</div>
            <div className="stat-value">
              {roadData.average_speed ? roadData.average_speed.toFixed(0) : '—'}
            </div>
            <div className="stat-sub">{roadData.average_speed ? 'km/h' : 'no data'}</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon orange"><TrendingUp size={20} /></div>
          <div className="stat-content">
            <div className="stat-label">Congestion Score</div>
            <div className="stat-value">
              {roadData.congestion_score ? roadData.congestion_score.toFixed(1) : '—'}
            </div>
            <div className="stat-sub">out of 100</div>
          </div>
        </div>
      </div>

      {/* Chart */}
      {chartData.length > 0 ? (
        <div className="chart-card">
          <div className="chart-header">
            <h3>24-Hour Traffic Trends</h3>
            <span className="badge badge-info">Hourly</span>
          </div>
          <ResponsiveContainer width="100%" height={320}>
            <LineChart data={chartData} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
              <XAxis dataKey="time" tick={{ fontSize: 12, fill: '#94a3b8' }} />
              <YAxis yAxisId="left" tick={{ fontSize: 12, fill: '#94a3b8' }} />
              <YAxis yAxisId="right" orientation="right" tick={{ fontSize: 12, fill: '#94a3b8' }} />
              <Tooltip
                contentStyle={{
                  background: '#0f172a', border: 'none',
                  borderRadius: 8, color: '#f1f5f9', fontSize: 13,
                }}
              />
              <Legend wrapperStyle={{ fontSize: 13 }} />
              <Line yAxisId="left"  type="monotone" dataKey="vehicles" stroke="#3b82f6"
                name="Vehicle Count" strokeWidth={2} dot={false} activeDot={{ r: 5 }} />
              <Line yAxisId="right" type="monotone" dataKey="speed"    stroke="#10b981"
                name="Avg Speed (km/h)" strokeWidth={2} dot={false} activeDot={{ r: 5 }} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      ) : (
        <div className="chart-card">
          <div className="chart-header"><h3>24-Hour Traffic Trends</h3></div>
          <div className="empty-state">
            <TrendingUp size={36} />
            <h3>No trend data yet</h3>
            <p>Traffic records will appear here once data is collected.</p>
          </div>
        </div>
      )}
    </div>
  )
}
