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
  SocialPlatform,
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

function unwrapData(data: unknown): unknown {
  if (data && typeof data === 'object' && 'data' in (data as object) && 'error' in (data as object)) {
    return (data as { data: unknown }).data
  }
  return data
}

function sessionFrom(payload: Record<string, unknown>): Session {
  const access =
    (payload.accessToken as string) ||
    (payload.access_token as string) ||
    ''
  const user = (payload.user || {}) as Record<string, unknown>
  const contractor = (payload.contractor || {}) as Record<string, unknown>
  const company = (payload.company || {}) as Record<string, unknown>
  return {
    accessToken: access,
    contractor: {
      id: String(contractor.id || user.id || ''),
      companyId: String(contractor.companyId || company.id || ''),
      name: String(contractor.name || user.full_name || user.fullName || ''),
      email: String(contractor.email || user.email || ''),
      phone: String(contractor.phone || user.phone || ''),
      role: String(contractor.role || 'owner'),
    },
    company: companyFrom(company),
  }
}

function companyFrom(company: Record<string, unknown>): Company {
  const mins = (company.photoMinimums || company.photo_minimums || {}) as Record<string, number>
  const maxs = (company.photoMaximums || company.photo_maximums || {}) as Record<string, number>
  const notes = (company.notificationSettings || company.notification_settings || {}) as Record<string, boolean>
  return {
    id: String(company.id || ''),
    name: String(company.name || ''),
    contactName: String(company.contactName || company.contact_name || ''),
    phone: String(company.phone || ''),
    email: String(company.email || ''),
    website: String(company.website || company.website_url || ''),
    serviceArea: String(company.serviceArea || company.service_area || ''),
    photoMinimums: {
      before: Number(mins.before ?? 1),
      progress: Number(mins.progress ?? 0),
      after: Number(mins.after ?? 1),
    },
    photoMaximums: {
      before: Number(maxs.before ?? 15),
      progress: Number(maxs.progress ?? 30),
      after: Number(maxs.after ?? 15),
    },
    notificationSettings: {
      contentReadyForApproval: notes.contentReadyForApproval !== false,
      publishingComplete: notes.publishingComplete !== false,
    },
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
      const raw = (data || {}) as {
        code?: string
        message?: string
        fieldErrors?: Record<string, string>
        error?: { code?: string; message?: string; details?: { fieldErrors?: Record<string, string> } }
      }
      const nested = raw.error
      throw new HttpError(res.status, {
        code: nested?.code || raw.code,
        message: nested?.message || raw.message,
        fieldErrors: nested?.details?.fieldErrors || raw.fieldErrors,
      })
    }

    return unwrapData(data) as T
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
      const raw = await request<Record<string, unknown>>('POST', '/auth/login', {
        body: { email, password },
        auth: false,
      })
      const session = sessionFrom(raw)
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
        const raw = await request<Record<string, unknown>>('GET', '/auth/me')
        const session = sessionFrom(raw)
        if (session.accessToken) persistToken(session.accessToken)
        return session
      } catch {
        persistToken(null)
        return null
      }
    },

    async getCompany() {
      const raw = await request<Record<string, unknown>>('GET', '/company')
      return companyFrom(raw)
    },

    async updateCompany(input: UpdateCompanyInput) {
      const raw = await request<Record<string, unknown>>('PATCH', '/company', { body: input })
      return companyFrom(raw)
    },

    async updateNotificationSettings(settings: Company['notificationSettings']) {
      const raw = await request<Record<string, unknown>>('PATCH', '/company/settings', {
        body: settings,
      })
      return companyFrom(raw)
    },

    async listJobs(params?: ListJobsParams) {
      const raw = await request<{ items?: Job[]; nextCursor?: string | null } | Job[]>(
        'GET',
        '/jobs',
        {
          query: {
            status: params?.status,
            scope: params?.scope,
            cursor: params?.cursor,
          },
        },
      )
      if (Array.isArray(raw)) {
        return { items: raw, nextCursor: null }
      }
      return { items: raw.items || [], nextCursor: raw.nextCursor ?? null }
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
      try {
        const raw = await request<MediaAsset | Record<string, unknown> | null>(
          'GET',
          `/jobs/${jobId}/voice`,
        )
        if (!raw) return null
        if ((raw as MediaAsset).kind === 'audio' || (raw as MediaAsset).kind === 'photo') {
          return raw as MediaAsset
        }
        const v = raw as Record<string, unknown>
        const id = String(v.audio_asset_id || v.audioAssetId || v.id || '')
        if (!id) return null
        return {
          id,
          jobId,
          kind: 'audio' as const,
          photoCategory: null,
          url: String(v.audio_url || v.audioUrl || v.url || ''),
          thumbnailUrl: '',
          mimeType: String(v.mimeType || v.mime_type || 'audio/webm'),
          byteSize: Number(v.byteSize || v.file_size_bytes || 0),
          durationMs: (v.durationMs as number | null) ?? null,
          uploadStatus: 'complete' as const,
          isFavorite: false,
          isDeleted: false,
          version: 1,
          createdAt: String(v.createdAt || v.created_at || new Date().toISOString()),
        }
      } catch (err) {
        if (err instanceof HttpError && (err.status === 404 || err.code === 'VOICE_NOT_FOUND')) {
          return null
        }
        throw err
      }
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

    async connectSocialAccount(platform: SocialPlatform, accountName: string) {
      return request<SocialConnection>('PUT', `/social/connections/${platform}`, {
        body: { accountName },
      })
    },

    async disconnectSocialAccount(platform: SocialPlatform) {
      return request<SocialConnection>('POST', `/social/connections/${platform}/disconnect`)
    },

    async getSocialConnectUrl() {
      return request<{ url: string; expiresAt: string }>('POST', '/social/connect-url')
    },
  }
}
