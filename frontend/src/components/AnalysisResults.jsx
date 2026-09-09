import { useState } from 'react'
import { ChevronDown } from 'lucide-react'
import { getToolMeta } from '../utils/toolMeta'
import StatusBadge from './StatusBadge'
import StatisticsTable from './StatisticsTable'
import CorrelationMatrix from './CorrelationMatrix'
import OutlierTable from './OutlierTable'
import InsightsList from './InsightsList'
import VisualizationResults from './VisualizationResults'
import DynamicValue from './DynamicValue'

/**
 * Picks the right renderer for a step's result based on its tool name.
 * Any tool not listed here — including ones the backend might add later —
 * falls through to the generic DynamicValue renderer, so nothing crashes
 * or gets silently dropped.
 */
function StepBody({ step }) {
  if (step.status === 'skipped') {
    return <p className="empty-state">{step.detail || 'This step was skipped.'}</p>
  }
  if (step.status === 'failed') {
    return <p className="empty-state">{step.error || 'This step failed to run.'}</p>
  }

  const result = step.result

  switch (step.tool) {
    case 'descriptive_statistics':
      return <StatisticsTable result={result} />
    case 'correlation_analysis':
      return <CorrelationMatrix result={result} />
    case 'outlier_detection':
      return <OutlierTable result={result} />
    case 'categorical_analysis':
      return (
        <div>
          <InsightsList insights={result?.categorical_insights} />
          {result?.note && (
            <p className="empty-state" style={{ marginTop: '0.6rem' }}>
              {result.note}
            </p>
          )}
        </div>
      )
    case 'distribution_visualization':
    case 'categorical_visualization':
      return <VisualizationResults result={result} />
    default:
      return <DynamicValue value={result} />
  }
}

function ResultCard({ step }) {
  const [open, setOpen] = useState(step.status === 'success')
  const { label, icon: Icon } = getToolMeta(step.tool)

  return (
    <div className="result-card">
      <button className="result-card-header" onClick={() => setOpen((o) => !o)} type="button">
        <div className="result-card-header-left">
          <Icon size={17} />
          <div>
            <div className="result-card-title">{label}</div>
            <div className="result-card-reason">{step.reason}</div>
          </div>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <StatusBadge status={step.status} />
          <ChevronDown size={16} className={`result-card-toggle${open ? ' open' : ''}`} />
        </div>
      </button>
      {open && (
        <div className="result-card-body">
          <StepBody step={step} />
        </div>
      )}
    </div>
  )
}

export default function AnalysisResults({ results }) {
  if (!results || results.length === 0) {
    return <p className="empty-state">No results yet.</p>
  }

  return (
    <div className="fade-in-once">
      {results.map((step) => (
        <ResultCard step={step} key={`${step.step}-${step.tool}`} />
      ))}
    </div>
  )
}
