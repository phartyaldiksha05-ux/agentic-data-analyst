import DynamicValue from './DynamicValue'

/**
 * Expects tools.outliers.get_outlier_summary()'s shape:
 *   { columns_with_outliers, total_outliers, details: { <col>: { outlier_count, q1, q3, ... } } }
 */
export default function OutlierTable({ result }) {
  const details = result?.details

  if (!details || Object.keys(details).length === 0) {
    return <DynamicValue value={result} />
  }

  const columns = Object.keys(details)

  return (
    <div>
      <div className="data-table-wrap">
        <table className="data-table">
          <thead>
            <tr>
              <th>Column</th>
              <th>Outliers</th>
              <th>Lower bound</th>
              <th>Upper bound</th>
              <th>IQR</th>
            </tr>
          </thead>
          <tbody>
            {columns.map((col) => {
              const d = details[col] || {}
              return (
                <tr key={col}>
                  <td>{col}</td>
                  <td className="mono">{d.outlier_count ?? 0}</td>
                  <td className="mono">
                    {typeof d.lower_bound === 'number' ? d.lower_bound.toFixed(2) : '—'}
                  </td>
                  <td className="mono">
                    {typeof d.upper_bound === 'number' ? d.upper_bound.toFixed(2) : '—'}
                  </td>
                  <td className="mono">{typeof d.iqr === 'number' ? d.iqr.toFixed(2) : '—'}</td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
    </div>
  )
}
