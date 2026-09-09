import { useEffect, useState } from 'react'
import { Sparkles, Bot, Database, ListChecks } from 'lucide-react'
import Navbar from './components/Navbar'
import FileUpload from './components/FileUpload'
import DatasetOverview from './components/DatasetOverview'
import CleaningResults from './components/CleaningResults'
import AnalysisPlan from './components/AnalysisPlan'
import AnalysisResults from './components/AnalysisResults'
import Loading from './components/Loading'
import ErrorBanner from './components/ErrorBanner'
import { cleanDataset, getProfile, runAnalysis } from './services/api'

const STORAGE_KEY = 'agentic-data-analyst:dataset'
const THEME_KEY = 'agentic-data-analyst:theme'

export default function App() {
  const [uploadedFile, setUploadedFile] = useState(null) // { dataset_id, filename, profile }
  const [theme, setTheme] = useState(() => localStorage.getItem(THEME_KEY) || 'dark')

  const [cleaning, setCleaning] = useState({ loading: false, result: null, error: null })
  const [analysis, setAnalysis] = useState({ loading: false, result: null, error: null })

  // Apply the theme to the document root so CSS variables in index.css switch.
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme)
    localStorage.setItem(THEME_KEY, theme)
  }, [theme])

  function handleToggleTheme() {
    setTheme((t) => (t === 'dark' ? 'light' : 'dark'))
  }

  // Restore a previous session on load, so a page refresh doesn't lose the
  // dataset_id the backend requires for every later call.
  useEffect(() => {
    const saved = localStorage.getItem(STORAGE_KEY)
    if (!saved) return
    try {
      const { dataset_id, filename } = JSON.parse(saved)
      if (!dataset_id) return
      getProfile(dataset_id)
        .then((profile) => {
          setUploadedFile({ dataset_id, filename, profile })
        })
        .catch(() => {
          // Dataset no longer exists on the backend (e.g. server restarted) — drop it.
          localStorage.removeItem(STORAGE_KEY)
        })
    } catch {
      localStorage.removeItem(STORAGE_KEY)
    }
  }, [])

  function handleUploaded(data) {
    setUploadedFile(data)
    setCleaning({ loading: false, result: null, error: null })
    setAnalysis({ loading: false, result: null, error: null })
    localStorage.setItem(
      STORAGE_KEY,
      JSON.stringify({ dataset_id: data.dataset_id, filename: data.filename })
    )
  }

  function handleReset() {
    setUploadedFile(null)
    setCleaning({ loading: false, result: null, error: null })
    setAnalysis({ loading: false, result: null, error: null })
    localStorage.removeItem(STORAGE_KEY)
  }

  async function handleClean() {
    if (!uploadedFile) return
    setCleaning({ loading: true, result: null, error: null })
    try {
      const data = await cleanDataset(uploadedFile.dataset_id)
      setCleaning({ loading: false, result: data, error: null })
    } catch (err) {
      setCleaning({ loading: false, result: null, error: err.message })
    }
  }

  async function handleAnalyze() {
    if (!uploadedFile) return
    setAnalysis({ loading: true, result: null, error: null })
    try {
      const data = await runAnalysis(uploadedFile.dataset_id)
      setAnalysis({ loading: false, result: data, error: null })
    } catch (err) {
      setAnalysis({ loading: false, result: null, error: err.message })
    }
  }

  const anyLoading = cleaning.loading || analysis.loading
  // Prefer the freshest known profile: post-cleaning if available, otherwise the upload profile.
  const currentProfile = cleaning.result?.profile_after_cleaning || uploadedFile?.profile

  return (
    <div className="app-shell">
      <Navbar theme={theme} onToggleTheme={handleToggleTheme} />

      <div className="container">
        <section className="section">
          <div className="section-heading">
            <Database size={19} />
            <h2>Upload your dataset</h2>
          </div>
          <FileUpload uploadedFile={uploadedFile} onUploaded={handleUploaded} onReset={handleReset} />
        </section>

        {uploadedFile && (
          <>
            <section className="section">
              <div className="section-heading">
                <ListChecks size={19} />
                <h2>Dataset overview</h2>
              </div>
              <DatasetOverview profile={currentProfile} />

              <div className="action-row">
                <button className="btn" onClick={handleClean} disabled={anyLoading} type="button">
                  <Sparkles size={15} />
                  Clean dataset
                </button>
                <button
                  className="btn btn-agent"
                  onClick={handleAnalyze}
                  disabled={anyLoading}
                  type="button"
                >
                  <Bot size={15} />
                  Run AI analysis
                </button>
              </div>

              {cleaning.loading && (
                <div style={{ marginTop: '1rem' }}>
                  <Loading stage="clean" />
                </div>
              )}
              <ErrorBanner message={cleaning.error} />
            </section>

            {cleaning.result && (
              <section className="section">
                <div className="section-heading">
                  <Sparkles size={19} />
                  <h2>Cleaning results</h2>
                </div>
                <CleaningResults result={cleaning.result} />
              </section>
            )}

            {analysis.loading && (
              <section className="section">
                <Loading stage="analyze" />
              </section>
            )}
            <ErrorBanner message={analysis.error} />

            {analysis.result && (
              <>
                <section className="section">
                  <div className="section-heading agent">
                    <Bot size={19} />
                    <h2>AI analysis plan</h2>
                  </div>
                  <p className="section-sub" style={{ marginTop: '-0.9rem', marginBottom: '1.25rem' }}>
                    The steps below were chosen automatically based on this dataset's profile.
                  </p>
                  <AnalysisPlan plan={analysis.result.analysis_plan} />
                </section>

                <section className="section">
                  <div className="section-heading">
                    <ListChecks size={19} />
                    <h2>Analysis results</h2>
                  </div>
                  <AnalysisResults results={analysis.result.results} />
                </section>
              </>
            )}
          </>
        )}
      </div>
    </div>
  )
}
