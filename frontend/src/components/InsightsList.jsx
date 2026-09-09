import { Lightbulb } from 'lucide-react'

/**
 * Renders a list of insight strings (e.g. from categorical_analysis /
 * tools.insights.generate_categorical_insights). Insights are always taken
 * from the API response — nothing here is hardcoded copy.
 */
export default function InsightsList({ insights }) {
  if (!insights || insights.length === 0) {
    return <p className="empty-state">No insights were generated for this step.</p>
  }

  return (
    <div className="insight-list">
      {insights.map((text, i) => (
        <div className="insight-item" key={i}>
          <Lightbulb />
          <span>{text}</span>
        </div>
      ))}
    </div>
  )
}
