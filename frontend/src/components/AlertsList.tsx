import { Alert } from '@/types'
import { format } from 'date-fns'
import { AlertTriangle, Info, Zap } from 'lucide-react'

interface AlertsListProps {
  alerts: Alert[]
}

const SEVERITY_CONFIG: Record<string, { icon: React.ReactNode; cls: string; badge: string }> = {
  info:     { icon: <Info size={14} />,         cls: 'info',     badge: 'badge-info' },
  warning:  { icon: <AlertTriangle size={14} />, cls: 'warning',  badge: 'badge-warning' },
  critical: { icon: <Zap size={14} />,           cls: 'critical', badge: 'badge-danger' },
}

export default function AlertsList({ alerts }: AlertsListProps) {
  if (!alerts.length) {
    return (
      <div className="empty-state">
        <Info size={36} />
        <h3>No active alerts</h3>
        <p>All roads are operating normally.</p>
      </div>
    )
  }

  return (
    <div className="alerts-list">
      {alerts.map((alert) => {
        const config = SEVERITY_CONFIG[alert.severity] ?? SEVERITY_CONFIG.info
        return (
          <div key={alert.id} className={`alert-item ${config.cls}`}>
            <div className="alert-icon">{config.icon}</div>
            <div className="alert-content">
              <div className="alert-title">{alert.title}</div>
              {alert.message && <div className="alert-message">{alert.message}</div>}
              <div className="alert-meta">
                <span className={`badge ${config.badge}`}>{alert.severity.toUpperCase()}</span>
                <span className="alert-time">
                  {format(new Date(alert.created_at), 'MMM dd, HH:mm')}
                </span>
              </div>
            </div>
          </div>
        )
      })}
    </div>
  )
}
