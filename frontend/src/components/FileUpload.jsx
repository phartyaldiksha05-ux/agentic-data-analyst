import { useCallback, useRef, useState } from 'react'
import { UploadCloud, FileCheck2, RotateCcw } from 'lucide-react'
import { uploadDataset } from '../services/api'
import Loading from './Loading'
import ErrorBanner from './ErrorBanner'

/**
 * Handles the upload step end-to-end: drag-and-drop or click-to-browse,
 * calls POST /upload, and reports the result up to App. Once a dataset is
 * uploaded, shows a compact summary with a "Start over" option instead of
 * the drop zone.
 */
export default function FileUpload({ uploadedFile, onUploaded, onReset }) {
  const [dragging, setDragging] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const inputRef = useRef(null)

  const handleFile = useCallback(
    async (file) => {
      if (!file) return
      if (!file.name.toLowerCase().endsWith('.csv')) {
        setError('Please upload a .csv file.')
        return
      }
      setError(null)
      setLoading(true)
      try {
        const data = await uploadDataset(file)
        onUploaded(data)
      } catch (err) {
        setError(err.message)
      } finally {
        setLoading(false)
      }
    },
    [onUploaded]
  )

  const handleDrop = useCallback(
    (e) => {
      e.preventDefault()
      setDragging(false)
      const file = e.dataTransfer.files?.[0]
      handleFile(file)
    },
    [handleFile]
  )

  if (uploadedFile) {
    return (
      <div className="upload-summary fade-in-once">
        <div className="upload-summary-left">
          <FileCheck2 size={20} />
          <div>
            <div className="upload-summary-name">{uploadedFile.filename} — upload successful</div>
            <div className="upload-summary-id">Dataset ID: {uploadedFile.dataset_id}</div>
          </div>
        </div>
        <button className="btn-text" onClick={onReset} type="button">
          <RotateCcw size={13} style={{ verticalAlign: '-2px', marginRight: '4px' }} />
          Start over
        </button>
      </div>
    )
  }

  return (
    <div>
      <div
        className={`upload-card${dragging ? ' dragging' : ''}`}
        onDragOver={(e) => {
          e.preventDefault()
          setDragging(true)
        }}
        onDragLeave={() => setDragging(false)}
        onDrop={handleDrop}
      >
        <div className="upload-icon-wrap">
          <UploadCloud size={24} />
        </div>
        <div className="upload-title">Upload your dataset</div>
        <p className="upload-subtitle">
          Upload a CSV file and let our AI Agent analyze your data automatically.
        </p>
        <input
          ref={inputRef}
          type="file"
          accept=".csv"
          onChange={(e) => handleFile(e.target.files?.[0])}
        />
        <button
          className="btn btn-primary"
          type="button"
          onClick={() => inputRef.current?.click()}
          disabled={loading}
        >
          Choose CSV file
        </button>
      </div>
      {loading && (
        <div style={{ marginTop: '1rem' }}>
          <Loading stage="upload" />
        </div>
      )}
      <ErrorBanner message={error} />
    </div>
  )
}
