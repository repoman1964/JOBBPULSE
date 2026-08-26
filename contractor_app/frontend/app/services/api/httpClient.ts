import type { ApiClient, ListJobsParams, RevisionInput, SubmitJobInput } from './client'
import type {
  Company,
  ContentPackage,
  CreateJobInput,
  GeneratedAsset,
  Job,
  MediaAsset,
  PhotoCategory,
  Session,
  SocialConnection,
  UpdateCompanyInput,
  UploadSession,
} from '~/types/domain'

class HttpError extends Error {
  code: string
  fieldErrors?: Record<string, string>
  status: number

  constructor(
    status: number,
    body: { code?: string; message?: string; fieldErrors?: Record<string, string> },
  ) {
    super(body.message || 'Request failed')
    this.status = status
    this.code = body.code || 'http_error'
    this.fieldErrors = body.fieldErrors
  }
}

function joinUrl(base: string, path: string): string {
  const b = base.replace(/\/$/, '')
  const p = path.startsWith('/') ? path : `/${path}`
  return `${b}${p}`
}

function isLoopbackHostname(hostname: string): boolean {
  return hostname === 'localhost' || hostname === '127.0.0.1' || hostname === '::1' || hostname === '[::1]'
}

/** Browser calls to a loopback engine go same-origin so Vite can proxy (LAN/phone-safe). */
export function resolveEngineApiBase(configured: string, pageOrigin: string): string {
  const fallback = configured.trim() || pageOrigin
  try {
    const u = new URL(fallback, pageOrigin)
    const origin = isLoopbackHostname(u.hostname) ? new URL(pageOrigin).origin : u.origin
    return joinUrl(origin, '/api/v1')
  } catch {
    return joinUrl(pageOrigin, '/api/v1')
  }
}

export function createHttpApiClient(baseUrl: string): ApiClient {
  const pageOrigin = import.meta.client ? window.location.origin : 'http://localhost'
  const apiBase = resolveEngineApiBase(baseUrl, pageOrigin)
  let accessToken: string | null = null

  if (import.meta.client) {
    try {
      accessToken = localStorage.getItem('jp.accessToken')
    } catch {
      accessToken = null
    }
  }

  const persistToken = (token: string | null) => {
    accessToken = token
    if (!import.meta.client) return
    try {
      if (token) localStorage.setItem('jp.accessToken', token)
      else localStorage.removeItem('jp.accessToken')
    } catch {
      /* ignore */
    }
  }

  async function request<T>(
    method: string,
    path: string,
    options: {
      body?: unknown
      query?: Record<string, string | undefined>
      auth?: boolean
    } = {},
  ): Promise<T> {
    const u = new URL(joinUrl(apiBase, path), pageOrigin)
    if (options.query) {
      for (const [k, v] of Object.entries(options.query)) {
        if (v !== undefined && v !== '') u.searchParams.set(k, v)
      }
    }

    const headers: Record<string, string> = {
      Accept: 'application/json',
    }
    if (options.body !== undefined) {
      headers['Content-Type'] = 'application/json'
    }
    if (options.auth !== false && accessToken) {
      headers.Authorization = `Bearer ${accessToken}`
    }

    let res: Response
    try {
      res = await fetch(u.toString(), {
        method,
        headers,
        credentials: 'include',
        body: options.body !== undefined ? JSON.stringify(options.body) : undefined,
      })
    } catch {
      throw new HttpError(0, {
        code: 'network_error',
        message:
          'Could not reach the JobbPulse API. Confirm the backend is running (`make up`) and you are not blocked by CORS.',
      })
    }

    if (res.status === 204) {
      return undefined as T
    }

    const text = await res.text()
    let data: unknown = null
    if (text) {
      try {
        data = JSON.parse(text)
      } catch {
        data = { message: text }
      }
    }

    if (!res.ok) {
      const errBody = (data || {}) as {
        code?: string
        message?: string
        fieldErrors?: Record<string, string>
      }
      throw new HttpError(res.status, errBody)
    }

    return data as T
  }

  return {
    async register(input: {
      name: string
      email: string
      password: string
      companyName: string
      phone?: string
    }) {
      return request<{
        email: string
        companyId: string
        contractorId: string
        verificationUrl?: string
      }>('POST', '/auth/register', {
        body: input,
        auth: false,
      })
    },

    async login(email: string, password: string) {
      const session = await request<Session>('POST', '/auth/login', {
        body: { email, password },
        auth: false,
      })
      persistToken(session.accessToken)
      return session
    },

    async verifyEmail(token: string) {
      return request<{ email: string; verified: boolean }>('POST', '/auth/verify-email', {
        body: { token },
        auth: false,
      })
    },

    async resendVerification(email: string) {
      await request<void>('POST', '/auth/resend-verification', {
        body: { email },
        auth: false,
      })
    },

    async logout() {
      try {
        await request<void>('POST', '/auth/logout', { auth: false })
      } finally {
        persistToken(null)
      }
    },

    async getSession() {
      if (!accessToken) return null
      try {
        const session = await request<Session>('GET', '/auth/me')
        if (session.accessToken) persistToken(session.accessToken)
        return session
      } catch {
        persistToken(null)
        return null
      }
    },

    async getCompany() {
      return request<Company>('GET', '/company')
    },

    async updateCompany(input: UpdateCompanyInput) {
      return request<Company>('PATCH', '/company', { body: input })
    },

    async updateNotificationSettings(settings: Company['notificationSettings']) {
      return request<Company>('PATCH', '/company/settings', { body: settings })
    },

    async listJobs(params?: ListJobsParams) {
      return request<{ items: Job[]; nextCursor: string | null }>('GET', '/jobs', {
        query: { status: params?.status, cursor: params?.cursor },
      })
    },

    async getJob(jobId: string) {
      return request<Job>('GET', `/jobs/${jobId}`)
    },

    async createJob(input: CreateJobInput) {
      return request<Job>('POST', '/jobs', { body: input })
    },

    async updateJob(jobId: string, input: Partial<CreateJobInput>) {
      return request<Job>('PATCH', `/jobs/${jobId}`, { body: input })
    },

    async deleteJob(jobId: string) {
      await request<void>('DELETE', `/jobs/${jobId}`)
    },

    async submitJob(jobId: string, input: SubmitJobInput) {
      return request<Job>('POST', `/jobs/${jobId}/submit`, { body: input })
    },

    async createPhotoUploadSession(
      jobId: string,
      category: PhotoCategory,
      meta: { mimeType: string; byteSize: number; filename?: string },
    ) {
      return request<UploadSession>('POST', `/jobs/${jobId}/media/upload-sessions`, {
        body: {
          category,
          mimeType: meta.mimeType,
          byteSize: meta.byteSize,
          filename: meta.filename,
        },
      })
    },

    async completeMediaUpload(jobId: string, mediaId: string, _localObjectUrl?: string) {
      return request<MediaAsset>('POST', `/jobs/${jobId}/media/${mediaId}/complete`)
    },

    async createVoiceUploadSession(
      jobId: string,
      meta: { mimeType: string; byteSize: number; durationMs: number },
    ) {
      return request<UploadSession>('POST', `/jobs/${jobId}/voice/upload-sessions`, {
        body: {
          mimeType: meta.mimeType,
          byteSize: meta.byteSize,
          durationMs: meta.durationMs,
        },
      })
    },

    async completeVoiceUpload(jobId: string, mediaId: string, _localObjectUrl?: string) {
      return request<MediaAsset>('POST', `/jobs/${jobId}/voice/${mediaId}/complete`)
    },

    async getVoice(jobId: string) {
      return request<MediaAsset | null>('GET', `/jobs/${jobId}/voice`)
    },

    async listMedia(jobId: string, category?: PhotoCategory) {
      return request<MediaAsset[]>('GET', `/jobs/${jobId}/media`, {
        query: { category },
      })
    },

    async updateMedia(
      jobId: string,
      mediaId: string,
      patch: { isFavorite?: boolean; photoCategory?: PhotoCategory },
    ) {
      return request<MediaAsset>('PATCH', `/jobs/${jobId}/media/${mediaId}`, { body: patch })
    },

    async deleteMedia(jobId: string, mediaId: string) {
      await request<void>('DELETE', `/jobs/${jobId}/media/${mediaId}`)
    },

    async getPackage(jobId: string) {
      return request<ContentPackage | null>('GET', `/jobs/${jobId}/package`)
    },

    async updateFeaturedMedia(
      jobId: string,
      featuredBeforeMediaId: string,
      featuredAfterMediaId: string,
    ) {
      return request<ContentPackage>('PATCH', `/jobs/${jobId}/package/featured-media`, {
        body: { featuredBeforeMediaId, featuredAfterMediaId },
      })
    },

    async requestDescriptionRevision(jobId: string, instructionText: string) {
      return request<ContentPackage>('POST', `/jobs/${jobId}/package/description-revision`, {
        body: { instructionText },
      })
    },

    async getGeneratedAsset(assetId: string) {
      return request<GeneratedAsset>('GET', `/generated-assets/${assetId}`)
    },

    async requestAssetRevision(assetId: string, input: RevisionInput) {
      return request<GeneratedAsset>('POST', `/generated-assets/${assetId}/revisions`, {
        body: input,
      })
    },

    async selectAssetVersion(assetId: string, versionId: string) {
      return request<GeneratedAsset>('POST', `/generated-assets/${assetId}/select-version`, {
        body: { versionId },
      })
    },

    async approveAndPublish(jobId: string, idempotencyKey: string) {
      return request<Job>('POST', `/jobs/${jobId}/approve-and-publish`, {
        body: { idempotencyKey },
      })
    },

    async listSocialConnections() {
      return request<SocialConnection[]>('GET', '/social/connections')
    },

    async getSocialConnectUrl() {
      return request<{ url: string; expiresAt: string }>('POST', '/social/connect-url')
    },
  }
}
