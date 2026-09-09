import DatasetOverview from './DatasetOverview'

/**
 * Renders the response of POST /clean/{dataset_id}:
 * { cleaning_summary: {...}, profile_after_cleaning: {...} }
 * Both fields are read defensively since a minimal or older backend build
 * might omit profile_after_cleaning.
 */
export default function CleaningResults({ result }) {
  if (!result) return null

  const summary = result.cleaning_summary || {}
  const {
    rows_before,
    rows_after,
    duplicates_removed,
    missing_values_before,
    missing_values_after,
  } = summary

  const rows = [
    ['Rows before', rows_before],
    ['Rows after', rows_after],
    ['Duplicates removed', duplicates_removed],
    ['Missing values before', missing_values_before],
    ['Missing values after', missing_values_after],
  ].filter(([, value]) => value !== undefined)

  return (
    <div className="fade-in-once">
      {rows.length === 0 ? (
        <p className="empty-state">No cleaning summary was returned.</p>
      ) : (
        <div className="data-table-wrap" style={{ marginBottom: '1.25rem' }}>
          <table className="data-table">
            <tbody>
              {rows.map(([label, value]) => (
                <tr key={label}>
                  <th style={{ width: '55%' }}>{label}</th>
                  <td className="mono">{value}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {result.profile_after_cleaning && (
        <>
          <h3 style={{ fontSize: '0.95rem', marginBottom: '0.85rem' }}>Profile after cleaning</h3>
          <DatasetOverview profile={result.profile_after_cleaning} />
        </>
      )}
    </div>
  )
}
