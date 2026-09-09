import axios from 'axios'

// Base URL of the existing FastAPI backend. Override via a .env file
// (VITE_API_BASE_URL=http://your-host:8000) without touching this file.
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'

const client = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000, // analysis can take a few seconds on larger datasets
})

/**
 * Turn any axios error into a short, user-friendly message.
 * Never surfaces raw stack traces or technical noise to the UI.
 */
function toFriendlyError(error, fallbackMessage) {
  if (error.response) {
    // Backend responded with an error status.
    const detail = error.response.data?.detail
    if (typeof detail === 'string') return detail
    if (error.response.status === 404) return 'Dataset not found.'
    if (error.response.status === 422) return 'The dataset could not be processed. Please check the file and try again.'
    return fallbackMessage
  }
  if (error.request) {
    // Request was made but no response received (backend down / CORS / offline).
    return 'Could not reach the backend. Make sure the API server is running.'
  }
  return fallbackMessage
}

/**
 * Upload a CSV file.
 * Backend: POST /upload
 * Returns: { dataset_id, filename, profile }
 */
export async function uploadDataset(file) {
  const formData = new FormData()
  formData.append('file', file)

  try {
    const response = await client.post('/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return response.data
  } catch (error) {
    throw new Error(toFriendlyError(error, 'Upload failed. Please try again.'))
  }
}

/**
 * Fetch the current profile for a dataset.
 * Backend: GET /profile/{dataset_id}
 */
export async function getProfile(datasetId) {
  try {
    const response = await client.get(`/profile/${datasetId}`)
    return response.data
  } catch (error) {
    throw new Error(toFriendlyError(error, 'Could not load the dataset profile.'))
  }
}

/**
 * Run the existing cleaning pipeline on a dataset.
 * Backend: POST /clean/{dataset_id}
 */
export async function cleanDataset(datasetId) {
  try {
    const response = await client.post(`/clean/${datasetId}`)
    return response.data
  } catch (error) {
    throw new Error(toFriendlyError(error, 'Cleaning failed. Please try again.'))
  }
}

/**
 * Run the full AI Agent analysis pipeline on a dataset.
 * Backend: POST /analyze/{dataset_id}
 */
export async function runAnalysis(datasetId) {
  try {
    const response = await client.post(`/analyze/${datasetId}`)
    return response.data
  } catch (error) {
    throw new Error(toFriendlyError(error, 'Analysis failed. Please try again.'))
  }
}

/**
 * Lightweight check used only to show an "online/offline" dot in the navbar.
 * Non-fatal if it fails — the rest of the app works independently of this.
 */
export async function checkHealth() {
  try {
    await client.get('/', { timeout: 3000 })
    return true
  } catch {
    return false
  }
}
