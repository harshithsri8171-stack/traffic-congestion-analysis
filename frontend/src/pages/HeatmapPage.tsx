import { useQuery } from '@tanstack/react-query'
import { MapContainer, TileLayer, CircleMarker, Popup } from 'react-leaflet'
import 'leaflet/dist/leaflet.css'
import { api } from '@/services/api'
import { useNavigate } from 'react-router-dom'
import { MapPin } from 'lucide-react'

const LEVEL_COLORS: Record<string, string> = {
  free_flow:  '#10b981',
  moderate:   '#f59e0b',
  congested:  '#f97316',
  severe:     '#ef4444',
}

const LEVEL_LABELS: Record<string, string> = {
  free_flow: 'Free Flow',
  moderate:  'Moderate',
  congested: 'Congested',
  severe:    'Severe',
}

const DEFAULT_CENTER: [number, number] = [17.385, 78.4867] // Hyderabad

export default function HeatmapPage() {
  const navigate = useNavigate()

  const { data: heatmapData, isLoading } = useQuery({
    queryKey: ['heatmap'],
    queryFn: () => api.getHeatmap(),
    refetchInterval: 60000,
  })

  const points: any[] = heatmapData?.points ?? []
  const hasCoords = points.some((p) => p.latitude && p.longitude)

  if (isLoading) {
    return (
      <div className="loading-page">
        <div className="spinner" />
        <span>Loading heatmap...</span>
      </div>
    )
  }

  const mapCenter: [number, number] = hasCoords
    ? [
        points.find((p) => p.latitude)?.latitude ?? DEFAULT_CENTER[0],
        points.find((p) => p.longitude)?.longitude ?? DEFAULT_CENTER[1],
      ]
    : DEFAULT_CENTER

  return (
    <div>
      <div className="page-header">
        <h1>Traffic Heatmap</h1>
        <p>Live congestion overview across all monitored road segments.</p>
      </div>

      <div className="heatmap-layout">
        {/* Map */}
        <div className="map-container">
          <MapContainer
            center={mapCenter}
            zoom={12}
            style={{ height: '100%', minHeight: 500, width: '100%' }}
          >
            <TileLayer
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />
            {points.map((point) => {
              if (!point.latitude || !point.longitude) return null
              const color = LEVEL_COLORS[point.congestion_level] ?? '#94a3b8'
              return (
                <CircleMarker
                  key={point.road_id}
                  center={[point.latitude, point.longitude]}
                  radius={16}
                  pathOptions={{
                    color,
                    fillColor: color,
                    fillOpacity: 0.75,
                    weight: 2,
                  }}
                >
                  <Popup>
                    <div style={{ minWidth: 160, fontFamily: 'Inter, sans-serif' }}>
                      <div style={{ fontWeight: 700, marginBottom: 6, fontSize: 14 }}>
                        {point.road_name}
                      </div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 4 }}>
                        <span style={{
                          background: color, color: 'white',
                          padding: '2px 8px', borderRadius: 999,
                          fontSize: 11, fontWeight: 600,
                        }}>
                          {LEVEL_LABELS[point.congestion_level] ?? point.congestion_level}
                        </span>
                      </div>
                      <div style={{ color: '#64748b', fontSize: 12 }}>
                        Score: {point.congestion_score?.toFixed(1) ?? 'N/A'}
                      </div>
                      <button
                        onClick={() => navigate(`/road/${point.road_id}`)}
                        style={{
                          marginTop: 8, padding: '4px 10px',
                          background: '#3b82f6', color: 'white',
                          border: 'none', borderRadius: 6,
                          fontSize: 12, cursor: 'pointer', fontWeight: 500,
                        }}
                      >
                        View Detail →
                      </button>
                    </div>
                  </Popup>
                </CircleMarker>
              )
            })}
          </MapContainer>
        </div>

        {/* Sidebar list */}
        <div>
          <div style={{ marginBottom: '1rem' }}>
            <h3 style={{ fontWeight: 600, fontSize: '0.9375rem', marginBottom: '0.5rem' }}>
              Road Status ({points.length})
            </h3>
            {/* Legend */}
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem', marginBottom: '0.75rem' }}>
              {Object.entries(LEVEL_LABELS).map(([key, label]) => (
                <div key={key} style={{ display: 'flex', alignItems: 'center', gap: '0.3rem', fontSize: '0.75rem' }}>
                  <span style={{ width: 10, height: 10, borderRadius: '50%', background: LEVEL_COLORS[key], display: 'inline-block' }} />
                  {label}
                </div>
              ))}
            </div>
          </div>

          <div className="heatmap-sidebar-list">
            {points.length === 0 ? (
              <div className="empty-state">
                <MapPin size={36} />
                <h3>No road data</h3>
                <p>Seed demo data from the Admin panel to see roads here.</p>
              </div>
            ) : (
              points.map((point) => {
                const color = LEVEL_COLORS[point.congestion_level] ?? '#94a3b8'
                return (
                  <div
                    key={point.road_id}
                    className="heatmap-road-item"
                    onClick={() => navigate(`/road/${point.road_id}`)}
                  >
                    <div className="heatmap-road-name">{point.road_name}</div>
                    <div className="heatmap-road-meta">
                      <span className="heatmap-score">
                        Score: {point.congestion_score?.toFixed(1) ?? '—'}
                      </span>
                      <span style={{
                        background: color + '22',
                        color,
                        padding: '2px 8px',
                        borderRadius: 999,
                        fontSize: '0.7rem',
                        fontWeight: 600,
                      }}>
                        {LEVEL_LABELS[point.congestion_level] ?? point.congestion_level}
                      </span>
                    </div>
                  </div>
                )
              })
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
