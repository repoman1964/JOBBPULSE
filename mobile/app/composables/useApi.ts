/**
 * JobPulse — API client composable.
 * Handles all communication with the FastAPI backend.
 */

export const useApi = () => {
  const config = useRuntimeConfig()
  const baseUrl = config.public.apiBase as string

  const request = async <T = any>(
    path: string,
    options: RequestInit = {}
  ): Promise<T> => {
    const url = `${baseUrl}${path}`
    const res = await fetch(url, {
      ...options,
      headers: {
        ...(options.body instanceof FormData ? {} : { 'Content-Type': 'application/json' }),
        ...options.headers,
      },
    })

    if (!res.ok) {
      const error = await res.json().catch(() => ({ detail: res.statusText }))
      throw new Error(error.detail || `API error: ${res.status}`)
    }

    return res.json()
  }

  // ── Jobs ─────────────────────────────────────────

  const createJob = async (formData: FormData) => {
    return request('/api/jobs', { method: 'POST', body: formData })
  }

  const getJobs = async (limit = 50, offset = 0) => {
    return request(`/api/jobs?limit=${limit}&offset=${offset}`)
  }

  const getJob = async (id: string) => {
    return request(`/api/jobs/${id}`)
  }

  const getStats = async () => {
    return request('/api/jobs/stats')
  }

  // ── Content ──────────────────────────────────────

  const generateContent = async (jobId: string, options?: { tone?: string; custom_instructions?: string }) => {
    return request(`/api/jobs/${jobId}/generate`, {
      method: 'POST',
      body: options ? JSON.stringify(options) : undefined,
    })
  }

  const editContent = async (jobId: string, contentId: string, edit: { title?: string; body?: string; hashtags?: string }) => {
    return request(`/api/jobs/${jobId}/content/${contentId}`, {
      method: 'PUT',
      body: JSON.stringify(edit),
    })
  }

  const publishContent = async (jobId: string, platforms?: string[]) => {
    return request(`/api/jobs/${jobId}/publish`, {
      method: 'POST',
      body: platforms ? JSON.stringify({ platforms }) : undefined,
    })
  }

  // ── Uploads URL ──────────────────────────────────

  const getPhotoUrl = (filePath: string) => {
    // Convert local path to served URL
    const relativePath = filePath.replace(/^\.\/uploads\//, '')
    return `${baseUrl}/uploads/${relativePath}`
  }

  return {
    createJob,
    getJobs,
    getJob,
    getStats,
    generateContent,
    editContent,
    publishContent,
    getPhotoUrl,
  }
}
