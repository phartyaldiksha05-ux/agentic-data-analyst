import {
  Sparkles,
  BarChart3,
  Tags,
  GitBranch,
  AreaChart,
  PieChart,
  AlertTriangle,
  Clock,
  Wrench,
} from 'lucide-react'

/**
 * Central lookup for every tool name the backend's AI Agent can plan.
 * Anything not in this map (a future tool, or a typo) safely falls back
 * to a generic entry rather than breaking the UI — the brief requires the
 * frontend to never assume a fixed, hardcoded set of tools.
 */
export const TOOL_META = {
  data_cleaning: { label: 'Data cleaning', icon: Sparkles },
  descriptive_statistics: { label: 'Descriptive statistics', icon: BarChart3 },
  categorical_analysis: { label: 'Categorical analysis', icon: Tags },
  correlation_analysis: { label: 'Correlation analysis', icon: GitBranch },
  distribution_visualization: { label: 'Distribution visualization', icon: AreaChart },
  categorical_visualization: { label: 'Categorical visualization', icon: PieChart },
  outlier_detection: { label: 'Outlier detection', icon: AlertTriangle },
  time_series_analysis: { label: 'Time series analysis', icon: Clock },
}

const FALLBACK_META = { label: null, icon: Wrench }

/**
 * Returns { label, icon } for a given tool name, humanizing unknown tool
 * names (e.g. "some_new_tool" -> "Some new tool") instead of failing.
 */
export function getToolMeta(toolName) {
  const known = TOOL_META[toolName]
  if (known) return known
  return {
    label: humanizeKey(toolName || 'unknown_tool'),
    icon: FALLBACK_META.icon,
  }
}

/** Converts a snake_case backend key into a readable label. */
export function humanizeKey(key) {
  if (!key) return ''
  return key
    .replace(/_/g, ' ')
    .replace(/\b\w/g, (c) => c.toUpperCase())
}
