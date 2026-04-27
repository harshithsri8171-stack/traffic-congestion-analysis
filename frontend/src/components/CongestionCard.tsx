import { CongestionLevel } from '@/types'

interface CongestionCardProps {
  level: CongestionLevel
  count: number
  label: string
}

const CONFIG = {
  [CongestionLevel.FREE_FLOW]:  { cls: 'free-flow',  emoji: '🟢' },
  [CongestionLevel.MODERATE]:   { cls: 'moderate',   emoji: '🟡' },
  [CongestionLevel.CONGESTED]:  { cls: 'congested',  emoji: '🟠' },
  [CongestionLevel.SEVERE]:     { cls: 'severe',     emoji: '🔴' },
}

export default function CongestionCard({ level, count, label }: CongestionCardProps) {
  const { cls, emoji } = CONFIG[level]
  return (
    <div className={`congestion-card ${cls}`}>
      <div className="congestion-card-label">{emoji} {label}</div>
      <div className="congestion-card-count">{count}</div>
      <div className="congestion-card-sub">roads monitored</div>
    </div>
  )
}
