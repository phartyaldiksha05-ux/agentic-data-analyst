/** A single labeled stat tile, e.g. "Rows — 5,000". */
export default function MetricTile({ icon: Icon, label, value, warn = false }) {
  return (
    <div className="metric-tile">
      <div className="metric-tile-label">
        {Icon && <Icon />}
        <span>{label}</span>
      </div>
      <div className={`metric-tile-value${warn ? ' warn' : ''}`}>{value}</div>
    </div>
  )
}
