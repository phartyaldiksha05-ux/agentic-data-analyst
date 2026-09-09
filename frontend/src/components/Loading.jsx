import { Bot } from 'lucide-react'

/**
 * A single reusable loading row. `stage` picks the message so each async
 * step of the workflow ("Uploading dataset...", "Cleaning dataset...",
 * "AI Agent is analyzing your dataset...") reads like a step in an AI
 * workflow rather than a generic spinner.
 */
const STAGE_MESSAGES = {
  upload: 'Uploading dataset…',
  clean: 'Cleaning dataset…',
  analyze: 'AI Agent is analyzing your dataset…',
}

export default function Loading({ stage, message }) {
  const text = message || STAGE_MESSAGES[stage] || 'Working…'
  const isAgentStage = stage === 'analyze'

  return (
    <div className="loading-row">
      {isAgentStage ? <Bot size={16} color="var(--agent)" /> : <span className="spinner" />}
      <span>{text}</span>
    </div>
  )
}
