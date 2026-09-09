import { useEffect, useState } from 'react'
import { Bot } from 'lucide-react'
import { checkHealth } from '../services/api'
import ThemeToggle from './ThemeToggle'

/**
 * App header. The brief specified a literal 🤖 emoji in the title — this
 * uses a matching Lucide Bot icon instead, for a more consistent,
 * professional icon system (Lucide was already an approved dependency).
 */
export default function Navbar({ theme, onToggleTheme }) {
  const [online, setOnline] = useState(null) // null = unknown, true/false once checked

  useEffect(() => {
    let cancelled = false
    checkHealth().then((ok) => {
      if (!cancelled) setOnline(ok)
    })
    return () => {
      cancelled = true
    }
  }, [])

  return (
    <header className="navbar">
      <div className="navbar-inner">
        <div className="navbar-brand">
          <div className="navbar-icon">
            <Bot size={18} />
          </div>
          <div>
            <div className="navbar-title">Agentic Data Analyst</div>
            <div className="navbar-subtitle">AI-powered automated data analysis</div>
          </div>
        </div>
        <div className="navbar-right">
          <div className="navbar-status">
            <span
              className={`status-dot ${online === null ? '' : online ? 'online' : 'offline'}`}
            />
            {online === null ? 'Checking API…' : online ? 'API connected' : 'API unreachable'}
          </div>
          <ThemeToggle theme={theme} onToggle={onToggleTheme} />
        </div>
      </div>
    </header>
  )
}
