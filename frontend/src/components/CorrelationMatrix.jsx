import DynamicValue from './DynamicValue'

/**
 * Expects tools.correlation.get_correlation_analysis()'s shape:
 *   { matrix: { <col>: { <col>: number } }, strong_positive: [...], strong_negative: [...] }
 * Renders the matrix as a proper grid and the strong-correlation lists
 * underneath. Falls back to the generic renderer if `matrix` is missing.
 */
export default function CorrelationMatrix({ result }) {
  const matrix = result?.matrix

  if (!matrix || Object.keys(matrix).length === 0) {
    return <DynamicValue value={result} />
  }

  const columns = Object.keys(matrix)
  const strongPositive = result?.strong_positive || []
  const strongNegative = result?.strong_negative || []

  return (
    <div>
      <div className="data-table-wrap" style={{ marginBottom: '1rem' }}>
        <table className="data-table">
          <thead>
            <tr>
              <th></th>
              {columns.map((c) => (
                <th key={c}>{c}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {columns.map((rowCol) => (
              <tr key={rowCol}>
                <th>{rowCol}</th>
                {columns.map((colCol) => {
                  const v = matrix[rowCol]?.[colCol]
                  return (
                    <td className="mono" key={colCol}>
                      {typeof v === 'number' ? v.toFixed(2) : '—'}
                    </td>
                  )
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {(strongPositive.length > 0 || strongNegative.length > 0) && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
          {strongPositive.map((item, i) => (
            <div key={`pos-${i}`} className="mono" style={{ fontSize: '0.85rem' }}>
              <DynamicValue value={item} />
            </div>
          ))}
          {strongNegative.map((item, i) => (
            <div key={`neg-${i}`} className="mono" style={{ fontSize: '0.85rem' }}>
              <DynamicValue value={item} />
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
