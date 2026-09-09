import { CheckCircle2, XCircle, MinusCircle } from 'lucide-react'

const STATUS_CONFIG = {
  success: { icon: CheckCircle2, label: 'Success', className: 'success' },
  failed: { icon: XCircle, label: 'Failed', className: 'failed' },
  skipped: { icon: MinusCircle, label: 'Skipped', className: 'skipped' },
}

/** Small color-coded status pill used across the plan and results sections. */
export default function StatusBadge({ status }) {
  const config = STATUS_CONFIG[status] || STATUS_CONFIG.skipped
  const Icon = config.icon
  return (
    <span className={`status-badge ${config.className}`}>
      <Icon />
      {config.label}
    </span>
  )
}
