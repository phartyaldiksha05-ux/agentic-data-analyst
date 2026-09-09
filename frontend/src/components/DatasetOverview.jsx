import { Rows3, Columns3, Hash, Tags, AlertTriangle, Copy } from 'lucide-react'
import MetricTile from './MetricTile'

/**
 * Renders the dataset profile: summary metric tiles + a per-column table.
 * Every field is read defensively (profile?.field ?? fallback) because the
 * exact shape can vary — a dataset with zero categorical columns, zero
 * missing values, etc. should render cleanly, not crash or show "undefined".
 */
export default function DatasetOverview({ profile }) {
  if (!profile) return null

  const {
    num_rows = 0,
    num_columns = 0,
    column_names = [],
    dtypes = {},
    missing_values = {},
    total_missing_values = 0,
    duplicate_rows = 0,
    unique_values = {},
    numerical_columns = [],
    categorical_columns = [],
  } = profile

  return (
    <div>
      <div className="metric-grid">
        <MetricTile icon={Rows3} label="Rows" value={num_rows.toLocaleString()} />
        <MetricTile icon={Columns3} label="Columns" value={num_columns} />
        <MetricTile icon={Hash} label="Numerical columns" value={numerical_columns.length} />
        <MetricTile icon={Tags} label="Categorical columns" value={categorical_columns.length} />
        <MetricTile
          icon={AlertTriangle}
          label="Missing values"
          value={total_missing_values}
          warn={total_missing_values > 0}
        />
        <MetricTile
          icon={Copy}
          label="Duplicate rows"
          value={duplicate_rows}
          warn={duplicate_rows > 0}
        />
      </div>

      {column_names.length === 0 ? (
        <p className="empty-state">No column information available.</p>
      ) : (
        <div className="data-table-wrap">
          <table className="data-table">
            <thead>
              <tr>
                <th>Column name</th>
                <th>Data type</th>
                <th>Missing values</th>
                <th>Unique values</th>
              </tr>
            </thead>
            <tbody>
              {column_names.map((name) => (
                <tr key={name}>
                  <td>{name}</td>
                  <td className="mono">{dtypes[name] ?? '—'}</td>
                  <td className="mono">{missing_values[name] ?? 0}</td>
                  <td className="mono">{unique_values[name] ?? '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
