/**
 * Thin API client for the JobPulse backend.
 */

type ApiEnvelope<T> = {
  data: T
  meta: Record<string, unknown>
  error: null | { code: string; message: string; details?: Record<string, unknown> }
}

export const useApi = () => {
  const config = useRuntimeConfig()
  const auth = useAuth()

  async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
    const headers: Record<string, string> = {
      ...(options.headers as Record<string, string> | undefined),
    }

    if (!(options.body instanceof FormData)) {
      headers['Content-Type'] = headers['Content-Type'] || 'application/json'
    }

    if (auth.accessToken.value) {
      headers.Authorization = `Bearer ${auth.accessToken.value}`
    }

    const res = await fetch(`${config.public.apiBase}${path}`, {
      ...options,
      headers,
    })

    const body = (await res.json().catch(() => null)) as ApiEnvelope<T> | null

    if (res.status === 401) {
      auth.clearSession()
      if (import.meta.client && !window.location.pathname.startsWith('/login')) {
        await navigateTo('/login')
      }
      throw new Error(body?.error?.message || 'Session expired. Please sign in again.')
    }

    if (!res.ok || body?.error) {
      throw new Error(body?.error?.message || `API error: ${res.status}`)
    }

    return body!.data
  }

  return {
    request,
    register: (payload: Record<string, unknown>) =>
      request('/api/v1/auth/register', { method: 'POST', body: JSON.stringify(payload) }),
    login: (payload: { email: string; password: string }) =>
      request('/api/v1/auth/login', { method: 'POST', body: JSON.stringify(payload) }),
    me: () => request('/api/v1/auth/me'),
    getCompany: () => request('/api/v1/company'),
    updateCompany: (payload: Record<string, unknown>) =>
      request('/api/v1/company', { method: 'PATCH', body: JSON.stringify(payload) }),
    getServices: () => request('/api/v1/company/services'),
    createService: (payload: Record<string, unknown>) =>
      request('/api/v1/company/services', { method: 'POST', body: JSON.stringify(payload) }),
    getServiceAreas: () => request('/api/v1/company/service-areas'),
    createServiceArea: (payload: Record<string, unknown>) =>
      request('/api/v1/company/service-areas', {
        method: 'POST',
        body: JSON.stringify(payload),
      }),

    // Jobs
    listJobs: (params?: { include_archived?: boolean }) => {
      const q = params?.include_archived ? '?include_archived=true' : ''
      return request(`/api/v1/jobs${q}`)
    },
    createJob: (payload: Record<string, unknown> = {}) =>
      request('/api/v1/jobs', { method: 'POST', body: JSON.stringify(payload) }),
    getJob: (jobId: string) => request(`/api/v1/jobs/${jobId}`),
    updateJob: (jobId: string, payload: Record<string, unknown>) =>
      request(`/api/v1/jobs/${jobId}`, { method: 'PATCH', body: JSON.stringify(payload) }),
    archiveJob: (jobId: string) =>
      request(`/api/v1/jobs/${jobId}/archive`, { method: 'POST' }),
    deleteJob: (jobId: string) =>
      request(`/api/v1/jobs/${jobId}`, { method: 'DELETE' }),

    // Media
    requestMediaUploadUrl: (jobId: string, payload: Record<string, unknown>) =>
      request(`/api/v1/jobs/${jobId}/media/upload-url`, {
        method: 'POST',
        body: JSON.stringify(payload),
      }),
    completeMediaUpload: (jobId: string, payload: Record<string, unknown>) =>
      request(`/api/v1/jobs/${jobId}/media/complete`, {
        method: 'POST',
        body: JSON.stringify(payload),
      }),
    uploadMediaDirect: async (jobId: string, file: File, stageLabel: string) => {
      const form = new FormData()
      form.append('file', file)
      form.append('stage_label', stageLabel)
      return request(`/api/v1/jobs/${jobId}/media/upload`, {
        method: 'POST',
        body: form,
      })
    },
    listJobMedia: (jobId: string) => request(`/api/v1/jobs/${jobId}/media`),
    updateMedia: (mediaId: string, payload: Record<string, unknown>) =>
      request(`/api/v1/media/${mediaId}`, {
        method: 'PATCH',
        body: JSON.stringify(payload),
      }),
    deleteMedia: (mediaId: string) =>
      request(`/api/v1/media/${mediaId}`, { method: 'DELETE' }),
    setPrimaryMedia: (mediaId: string) =>
      request(`/api/v1/media/${mediaId}/set-primary`, { method: 'POST' }),
    reorderMedia: (jobId: string, mediaIds: string[]) =>
      request(`/api/v1/jobs/${jobId}/media/reorder`, {
        method: 'POST',
        body: JSON.stringify({ media_ids: mediaIds }),
      }),
  }
}
