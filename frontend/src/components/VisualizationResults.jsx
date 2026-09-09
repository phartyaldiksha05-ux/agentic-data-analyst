import { ImageOff } from 'lucide-react'

/**
 * ASSUMPTION ABOUT THE BACKEND:
 * The orchestrator returns chart entries like:
 *   { type: "histogram", column: "sales", path: "backend/uploads/charts/histogram_sales.png" }
 * `path` is a local filesystem path on the backend host, not a URL — the
 * browser cannot load it directly (no static file route currently serves
 * `backend/uploads/charts/` over HTTP). Rather than guess at a URL that may
 * not exist and silently fail, this renders a clear placeholder per chart
 * and shows the raw path for reference/debugging.
 *
 * If/when the backend adds a static route (e.g. mounting `/charts` to serve
 * that folder), swap the placeholder below for:
 *   <img src={`${API_BASE_URL}/charts/${filenameFrom(chart.path)}`} alt={...} />
 */
export default function VisualizationResults({ result }) {
  const charts = result?.charts || []

  if (charts.length === 0) {
    return <p className="empty-state">No charts were generated for this step.</p>
  }

  return (
    <div className="chart-grid">
      {charts.map((chart, i) => (
        <div className="chart-placeholder" key={i}>
          <ImageOff size={20} className="chart-placeholder-icon" />
          <div className="chart-placeholder-type">{chart.type?.replace(/_/g, ' ')}</div>
          <div className="chart-placeholder-column">{chart.column}</div>
          <div className="chart-placeholder-note">
            Chart generated successfully. Backend chart serving endpoint required to preview it here.
          </div>
          {chart.path && <div className="chart-placeholder-path">{chart.path}</div>}
        </div>
      ))}
    </div>
  )
}
