import { AlertCircle } from 'lucide-react'

/**
 * Consistent, user-friendly error display. The `message` passed in should
 * already be friendly text (see services/api.js's toFriendlyError) — this
 * component never renders raw error objects or stack traces.
 */
export default function ErrorBanner({ message }) {
  if (!message) return null
  return (
    <div className="error-banner">
      <AlertCircle size={18} />
      <span>{message}</span>
    </div>
  )
}
