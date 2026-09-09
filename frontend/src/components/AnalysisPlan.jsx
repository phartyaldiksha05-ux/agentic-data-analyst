import { getToolMeta } from '../utils/toolMeta'

/**
 * Renders analysis_plan as a vertical timeline. Numbered steps are used
 * deliberately here (not decoratively) because the plan genuinely is a
 * sequence the Agent executes in order.
 */
export default function AnalysisPlan({ plan }) {
  if (!plan || plan.length === 0) {
    return <p className="empty-state">No analysis steps were planned for this dataset.</p>
  }

  return (
    <div className="plan-list fade-in-once">
      {plan.map((step, i) => {
        const { label, icon: Icon } = getToolMeta(step.tool)
        const isLast = i === plan.length - 1
        return (
          <div className="plan-step" key={`${step.step}-${step.tool}`}>
            <div className="plan-step-marker-col">
              <div className="plan-step-number">{step.step}</div>
              {!isLast && <div className="plan-step-line" />}
            </div>
            <div className="plan-step-body">
              <div className="plan-step-tool">
                <Icon />
                {label}
              </div>
              <div className="plan-step-reason">{step.reason}</div>
            </div>
          </div>
        )
      })}
    </div>
  )
}
