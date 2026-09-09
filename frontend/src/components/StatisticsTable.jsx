import DynamicValue from './DynamicValue'

/**
 * Expects tools.statistics.get_dataset_statistics()'s shape:
 *   { descriptive_statistics: { columns: { <col>: { count, mean, median, ... } } }, ... }
 * Renders columns as rows and stat names as columns, which reads far more
 * clearly than a generic key/value dump for this specific shape. Falls back
 * to the generic renderer if the expected keys aren't present, so a future
 * change to this tool's output doesn't break the page.
 */
export default function StatisticsTable({ result }) {
  const columns = result?.descriptive_statistics?.columns

  if (!columns || Object.keys(columns).length === 0) {
    return <DynamicValue value={result} />
  }

  const columnNames = Object.keys(columns)
  const statNames = Object.keys(columns[columnNames[0]] || {})

  return (
    <div className="data-table-wrap">
      <table className="data-table">
        <thead>
          <tr>
            <th>Column</th>
            {statNames.map((stat) => (
              <th key={stat}>{stat}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {columnNames.map((col) => (
            <tr key={col}>
              <td>{col}</td>
              {statNames.map((stat) => {
                const v = columns[col][stat]
                const display = typeof v === 'number' && !Number.isInteger(v) ? v.toFixed(2) : v
                return (
                  <td className="mono" key={stat}>
                    {display ?? '—'}
                  </td>
                )
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
