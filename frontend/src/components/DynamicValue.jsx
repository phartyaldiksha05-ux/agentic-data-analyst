import { humanizeKey } from '../utils/toolMeta'

/**
 * Renders an arbitrary JSON value (object, array, or primitive) without any
 * assumptions about its shape or the dataset's column names. Used as the
 * fallback whenever a tool's result doesn't have a bespoke component, and
 * for any future tool the backend adds that the frontend doesn't know about
 * yet.
 */
export default function DynamicValue({ value, depth = 0 }) {
  if (value === null || value === undefined) {
    return <span className="empty-state">Not available</span>
  }

  if (typeof value === 'number') {
    const rounded = Number.isInteger(value) ? value : Math.round(value * 10000) / 10000
    return <span className="mono">{rounded}</span>
  }

  if (typeof value === 'string' || typeof value === 'boolean') {
    return <span>{String(value)}</span>
  }

  if (Array.isArray(value)) {
    if (value.length === 0) {
      return <span className="empty-state">None</span>
    }
    // Array of primitives -> comma list. Array of objects -> mini key/value blocks.
    const allPrimitive = value.every((v) => typeof v !== 'object' || v === null)
    if (allPrimitive) {
      return <span className="mono">{value.join(', ')}</span>
    }
    return (
      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
        {value.map((item, i) => (
          <div
            key={i}
            style={{
              border: '1px solid var(--border)',
              borderRadius: 'var(--radius)',
              padding: '0.6rem 0.75rem',
            }}
          >
            <DynamicValue value={item} depth={depth + 1} />
          </div>
        ))}
      </div>
    )
  }

  if (typeof value === 'object') {
    const entries = Object.entries(value)
    if (entries.length === 0) {
      return <span className="empty-state">No data</span>
    }
    return (
      <div className="data-table-wrap">
        <table className="data-table">
          <tbody>
            {entries.map(([key, val]) => (
              <tr key={key}>
                <th style={{ width: '35%' }}>{humanizeKey(key)}</th>
                <td>
                  <DynamicValue value={val} depth={depth + 1} />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    )
  }

  return <span className="empty-state">Not available</span>
}
