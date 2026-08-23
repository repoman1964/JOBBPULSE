import type { ApiClient, ListJobsParams, RevisionInput, SubmitJobInput } from '../client'
import type {
  Company,
  ContentPackage,
  CreateJobInput,
  GeneratedAsset,
  Job,
  MediaAsset,
  PhotoCategory,
  PublicJobStatus,
  Session,
  SocialConnection,
  UpdateCompanyInput,
  UploadSession,
} from '~/types/domain'
import {
  SEED_COMPANY,
  SEED_CONTRACTOR,
  buildPackageForPaintJob,
  buildSeedJobs,
  buildSeedMedia,
  buildSeedSocial,
  placeholder,
} from './seed'
import { computePublicStatus, countsFromMedia, meetsMinimums } from '~/utils/jobStatus'

const STORAGE_KEY = 'jobbpulse.mock.v3'
const DEV_OTP = '123456'
const PROCESS_DELAY_MS = 2500

interface MockState {
  company: Company
  session: Session | null
  jobs: Job[]
  media: MediaAsset[]
  packages: ContentPackage[]
  social: SocialConnection[]
  challenges: Record<string, { identifier: string; code: string; expiresAt: number }>
  submitKeys: Set<string>
  publishKeys: Set<string>
}

function uid(prefix: string): string {
  return `${prefix}-${Math.random().toString(36).slice(2, 10)}`
}

function delay(ms = 120): Promise<void> {
  return new Promise((r) => setTimeout(r, ms))
}

function loadState(): MockState | null {
  if (!import.meta.client) return null
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (!raw) return null
    const parsed = JSON.parse(raw) as Omit<MockState, 'submitKeys' | 'publishKeys'> & {
      submitKeys: string[]
      publishKeys: string[]
    }
    return {
      ...parsed,
      submitKeys: new Set(parsed.submitKeys || []),
      publishKeys: new Set(parsed.publishKeys || []),
    }
  } catch {
    return null
  }
}

function persist(state: MockState) {
  if (!import.meta.client) return
  const payload = {
    ...state,
    submitKeys: [...state.submitKeys],
    publishKeys: [...state.publishKeys],
  }
  localStorage.setItem(STORAGE_KEY, JSON.stringify(payload))
}

function freshState(): MockState {
  const media = buildSeedMedia()
  const jobs = buildSeedJobs()
  const packages = [buildPackageForPaintJob(media)]
  return {
    company: structuredClone(SEED_COMPANY),
    session: null,
    jobs,
    media,
    packages,
    social: buildSeedSocial(),
    challenges: {},
    submitKeys: new Set(),
    publishKeys: new Set(),
  }
}

function recomputeJob(state: MockState, jobId: string) {
  const job = state.jobs.find((j) => j.id === jobId)
  if (!job) return
  const media = state.media.filter((m) => m.jobId === jobId && !m.isDeleted && m.kind === 'photo')
  job.counts = countsFromMedia(media)
  job.hasVoice = state.media.some(
    (m) => m.jobId === jobId && m.kind === 'audio' && !m.isDeleted && m.uploadStatus === 'complete',
  )
  const terminal: PublicJobStatus[] = [
    'processing',
    'ready_for_approval',
    'needs_revision',
    'publishing',
    'published',
    'publish_issue',
  ]
  if (!terminal.includes(job.publicStatus)) {
    job.publicStatus = computePublicStatus(job.counts, state.company.photoMinimums, job.hasVoice)
  }
  const cover =
    media.find((m) => m.photoCategory === 'after') ||
    media.find((m) => m.photoCategory === 'progress') ||
    media.find((m) => m.photoCategory === 'before')
  if (cover) job.coverUrl = cover.url
  job.updatedAt = new Date().toISOString()
}

function buildGeneratedPackage(state: MockState, job: Job): ContentPackage {
  const photos = state.media.filter((m) => m.jobId === job.id && m.kind === 'photo' && !m.isDeleted)
  const befores = photos.filter((m) => m.photoCategory === 'before')
  const afters = photos.filter((m) => m.photoCategory === 'after')
  const before = befores.find((m) => m.isFavorite) || befores[0]
  const after = afters.find((m) => m.isFavorite) || afters[0]
  const description = `We completed ${job.name} in ${job.locationText || job.city}. The crew documented the full transformation from start to finish.`

  const make = (
    dest: GeneratedAsset['destinationType'],
    title: string,
    body: string,
  ): GeneratedAsset => {
    const id = uid(`asset-${dest}`)
    const versionId = `${id}-v1`
    return {
      id,
      packageId: '',
      destinationType: dest,
      title,
      body,
      status: 'ready',
      activeVersionId: versionId,
      preview: {
        beforeUrl: before?.url,
        afterUrl: after?.url,
        coverUrl: after?.url || before?.url || job.coverUrl,
      },
      versions: [
        {
          id: versionId,
          version: 1,
          title,
          body,
          preview: {
            beforeUrl: before?.url,
            afterUrl: after?.url,
            coverUrl: after?.url || before?.url || job.coverUrl,
          },
          sourceMediaIds: [before?.id, after?.id].filter(Boolean) as string[],
          createdAt: new Date().toISOString(),
        },
      ],
    }
  }

  const pkgId = uid('pkg')
  const assets = [
    make('facebook', 'Facebook', `${job.name}: another transformation ready to share.`),
    make('instagram', 'Instagram', `${job.name} complete in ${job.city}. #JobbPulse`),
    make(
      'google_business',
      'Google Business Profile',
      `Just finished ${job.name} in ${job.city}. Solid prep, a clean finish, and a crew that shows up ready to work. Call us if you have a similar project.`,
    ),
    make('conversion_site', 'Project Page', description),
    make('portfolio_site', 'JobbPulse Portfolio', description),
  ].map((a) => ({ ...a, packageId: pkgId }))

  return {
    id: pkgId,
    jobId: job.id,
    version: 1,
    status: 'ready_for_approval',
    projectDescription: description,
    featuredBeforeMediaId: before?.id ?? null,
    featuredAfterMediaId: after?.id ?? null,
    assets,
  }
}

export function createMockApiClient(): ApiClient {
  let state = loadState() || freshState()

  // Restore session company pointer
  if (state.session) {
    state.session.company = state.company
    state.session.contractor = { ...SEED_CONTRACTOR, ...state.session.contractor }
  }

  const save = () => persist(state)

  const requireSession = () => {
    if (!state.session) {
      const err = new Error('Session expired. Please sign in again.') as Error & { code: string }
      err.code = 'session_expired'
      throw err
    }
    return state.session
  }

  const getJobOrThrow = (jobId: string) => {
    const job = state.jobs.find((j) => j.id === jobId && !j.deletedAt)
    if (!job) {
      const err = new Error('Job not found.') as Error & { code: string }
      err.code = 'not_found'
      throw err
    }
    return job
  }

  const scheduleProcessing = (jobId: string) => {
    setTimeout(() => {
      const job = state.jobs.find((j) => j.id === jobId)
      if (!job || job.deletedAt || job.publicStatus !== 'processing') return
      // Replace any existing package for this job
      state.packages = state.packages.filter((p) => p.jobId !== jobId)
      const pkg = buildGeneratedPackage(state, job)
      state.packages.push(pkg)
      job.publicStatus = 'ready_for_approval'
      job.updatedAt = new Date().toISOString()
      save()
    }, PROCESS_DELAY_MS)
  }

  const client: ApiClient = {
    async requestChallenge(identifier: string) {
      await delay()
      const challengeId = uid('challenge')
      state.challenges[challengeId] = {
        identifier: identifier.trim().toLowerCase(),
        code: DEV_OTP,
        expiresAt: Date.now() + 10 * 60 * 1000,
      }
      save()
      // Dev OTP always visible in mock mode
      console.info(`[JobbPulse mock auth] code for ${identifier}: ${DEV_OTP}`)
      return { challengeId, devCode: DEV_OTP }
    },

    async verifyChallenge(challengeId: string, code: string) {
      await delay()
      const challenge = state.challenges[challengeId]
      if (!challenge || challenge.expiresAt < Date.now()) {
        throw Object.assign(new Error('That code expired. Request a new one.'), {
          code: 'challenge_expired',
        })
      }
      if (code.trim() !== challenge.code && code.trim() !== DEV_OTP) {
        throw Object.assign(new Error('That code is incorrect. Try again.'), {
          code: 'invalid_code',
        })
      }
      delete state.challenges[challengeId]
      state.session = {
        accessToken: uid('tok'),
        contractor: structuredClone(SEED_CONTRACTOR),
        company: structuredClone(state.company),
      }
      save()
      return structuredClone(state.session)
    },

    async logout() {
      await delay(50)
      state.session = null
      save()
    },

    async getSession() {
      await delay(40)
      return state.session ? structuredClone(state.session) : null
    },

    async getCompany() {
      requireSession()
      await delay()
      return structuredClone(state.company)
    },

    async updateCompany(input: UpdateCompanyInput) {
      requireSession()
      await delay()
      state.company = { ...state.company, ...input }
      if (state.session) state.session.company = structuredClone(state.company)
      save()
      return structuredClone(state.company)
    },

    async updateNotificationSettings(settings) {
      requireSession()
      await delay()
      state.company.notificationSettings = { ...settings }
      if (state.session) state.session.company = structuredClone(state.company)
      save()
      return structuredClone(state.company)
    },

    async listJobs(_params?: ListJobsParams) {
      requireSession()
      await delay()
      const items = state.jobs
        .filter((j) => !j.deletedAt)
        .map((j) => {
          recomputeJob(state, j.id)
          return structuredClone(j)
        })
        .sort((a, b) => (a.updatedAt < b.updatedAt ? 1 : -1))
      save()
      return { items, nextCursor: null }
    },

    async getJob(jobId: string) {
      requireSession()
      await delay()
      recomputeJob(state, jobId)
      save()
      return structuredClone(getJobOrThrow(jobId))
    },

    async createJob(input: CreateJobInput) {
      requireSession()
      await delay()
      const job: Job = {
        id: uid('job'),
        companyId: state.company.id,
        name: input.name.trim(),
        serviceType: input.serviceType.trim(),
        city: input.city.trim(),
        region: (input.region || '').trim(),
        locationText:
          input.locationText?.trim() ||
          [input.city.trim(), (input.region || '').trim()].filter(Boolean).join(', '),
        internalNote: input.internalNote?.trim() || '',
        assignedCrewMember: input.assignedCrewMember?.trim() || '',
        publicStatus: 'active',
        coverUrl: null,
        counts: { before: 0, progress: 0, after: 0 },
        hasVoice: false,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        submittedAt: null,
        approvedAt: null,
        publishedAt: null,
      }
      state.jobs.unshift(job)
      save()
      return structuredClone(job)
    },

    async deleteJob(jobId: string) {
      requireSession()
      await delay()
      const job = getJobOrThrow(jobId)
      if (job.publicStatus === 'publishing') {
        throw Object.assign(new Error('Wait until publishing finishes before deleting this job.'), {
          code: 'job_locked',
        })
      }
      job.deletedAt = new Date().toISOString()
      job.updatedAt = job.deletedAt
      save()
    },

    async updateJob(jobId: string, input: Partial<CreateJobInput>) {
      requireSession()
      await delay()
      const job = getJobOrThrow(jobId)
      Object.assign(job, {
        ...input,
        updatedAt: new Date().toISOString(),
      })
      if (input.city || input.region) {
        job.locationText = [job.city, job.region].filter(Boolean).join(', ')
      }
      save()
      return structuredClone(job)
    },

    async submitJob(jobId: string, input: SubmitJobInput) {
      requireSession()
      await delay(200)
      if (state.submitKeys.has(input.idempotencyKey)) {
        return structuredClone(getJobOrThrow(jobId))
      }
      const job = getJobOrThrow(jobId)
      recomputeJob(state, jobId)
      if (!meetsMinimums(job.counts, state.company.photoMinimums)) {
        throw Object.assign(new Error('Add the required photos before submitting.'), {
          code: 'minimums_not_met',
        })
      }
      if (!job.hasVoice) {
        throw Object.assign(new Error('Record a short job description before submitting.'), {
          code: 'voice_required',
        })
      }
      const pending = state.media.some(
        (m) => m.jobId === jobId && !m.isDeleted && m.uploadStatus !== 'complete',
      )
      if (pending) {
        throw Object.assign(new Error('Wait for photo uploads to finish, then try again.'), {
          code: 'uploads_pending',
        })
      }
      state.submitKeys.add(input.idempotencyKey)
      job.publicStatus = 'processing'
      job.submittedAt = new Date().toISOString()
      job.updatedAt = job.submittedAt
      save()
      scheduleProcessing(jobId)
      return structuredClone(job)
    },

    async createPhotoUploadSession(jobId, category, meta) {
      requireSession()
      await delay(80)
      getJobOrThrow(jobId)
      const mediaId = uid('media')
      const asset: MediaAsset = {
        id: mediaId,
        jobId,
        kind: 'photo',
        photoCategory: category,
        url: '',
        thumbnailUrl: '',
        mimeType: meta.mimeType,
        byteSize: meta.byteSize,
        durationMs: null,
        uploadStatus: 'pending',
        isFavorite: false,
        isDeleted: false,
        version: 1,
        createdAt: new Date().toISOString(),
      }
      state.media.push(asset)
      save()
      return {
        mediaId,
        uploadUrl: `mock://upload/${mediaId}`,
        expiresAt: new Date(Date.now() + 15 * 60 * 1000).toISOString(),
      } satisfies UploadSession
    },

    async completeMediaUpload(jobId, mediaId, localObjectUrl) {
      requireSession()
      await delay(150)
      const asset = state.media.find((m) => m.id === mediaId && m.jobId === jobId)
      if (!asset) throw Object.assign(new Error('Upload not found.'), { code: 'not_found' })
      asset.uploadStatus = 'complete'
      asset.url = localObjectUrl || placeholder(mediaId, 900, 700)
      asset.thumbnailUrl = localObjectUrl || placeholder(mediaId, 400, 300)
      recomputeJob(state, jobId)
      save()
      return structuredClone(asset)
    },

    async createVoiceUploadSession(jobId, meta) {
      requireSession()
      await delay(80)
      getJobOrThrow(jobId)
      // Retire previous active voice
      state.media.forEach((m) => {
        if (m.jobId === jobId && m.kind === 'audio' && !m.isDeleted) {
          m.isDeleted = true
        }
      })
      const mediaId = uid('voice')
      const asset: MediaAsset = {
        id: mediaId,
        jobId,
        kind: 'audio',
        photoCategory: null,
        url: '',
        thumbnailUrl: '',
        mimeType: meta.mimeType,
        byteSize: meta.byteSize,
        durationMs: meta.durationMs,
        uploadStatus: 'pending',
        isFavorite: false,
        isDeleted: false,
        version: 1,
        createdAt: new Date().toISOString(),
      }
      state.media.push(asset)
      save()
      return {
        mediaId,
        uploadUrl: `mock://upload/${mediaId}`,
        expiresAt: new Date(Date.now() + 15 * 60 * 1000).toISOString(),
      }
    },

    async completeVoiceUpload(jobId, mediaId, localObjectUrl) {
      requireSession()
      await delay(150)
      const asset = state.media.find((m) => m.id === mediaId && m.jobId === jobId)
      if (!asset) throw Object.assign(new Error('Voice upload not found.'), { code: 'not_found' })
      asset.uploadStatus = 'complete'
      // Prefer durable data: URLs; blob: URLs die on reload
      asset.url = localObjectUrl || ''
      recomputeJob(state, jobId)
      save()
      return structuredClone(asset)
    },

    async getVoice(jobId) {
      requireSession()
      await delay(40)
      const asset = state.media.find(
        (m) =>
          m.jobId === jobId &&
          m.kind === 'audio' &&
          !m.isDeleted &&
          m.uploadStatus === 'complete',
      )
      return asset ? structuredClone(asset) : null
    },

    async listMedia(jobId, category) {
      requireSession()
      await delay(60)
      getJobOrThrow(jobId)
      return structuredClone(
        state.media.filter(
          (m) =>
            m.jobId === jobId &&
            !m.isDeleted &&
            m.kind === 'photo' &&
            (!category || m.photoCategory === category),
        ),
      )
    },

    async updateMedia(jobId, mediaId, patch) {
      requireSession()
      await delay(80)
      const asset = state.media.find((m) => m.id === mediaId && m.jobId === jobId && !m.isDeleted)
      if (!asset) throw Object.assign(new Error('Photo not found.'), { code: 'not_found' })
      if (typeof patch.isFavorite === 'boolean') asset.isFavorite = patch.isFavorite
      if (patch.photoCategory) asset.photoCategory = patch.photoCategory
      recomputeJob(state, jobId)
      save()
      return structuredClone(asset)
    },

    async deleteMedia(jobId, mediaId) {
      requireSession()
      await delay(80)
      const asset = state.media.find((m) => m.id === mediaId && m.jobId === jobId)
      if (!asset) return
      asset.isDeleted = true
      recomputeJob(state, jobId)
      save()
    },

    async getPackage(jobId) {
      requireSession()
      await delay()
      const pkg = state.packages.find((p) => p.jobId === jobId)
      return pkg ? structuredClone(pkg) : null
    },

    async updateFeaturedMedia(jobId, featuredBeforeMediaId, featuredAfterMediaId) {
      requireSession()
      await delay()
      const pkg = state.packages.find((p) => p.jobId === jobId)
      if (!pkg) throw Object.assign(new Error('Package not ready yet.'), { code: 'not_ready' })
      pkg.featuredBeforeMediaId = featuredBeforeMediaId
      pkg.featuredAfterMediaId = featuredAfterMediaId
      const before = state.media.find((m) => m.id === featuredBeforeMediaId)
      const after = state.media.find((m) => m.id === featuredAfterMediaId)
      for (const asset of pkg.assets) {
        asset.preview = {
          ...asset.preview,
          beforeUrl: before?.url,
          afterUrl: after?.url,
          coverUrl: after?.url || before?.url,
        }
      }
      save()
      return structuredClone(pkg)
    },

    async requestDescriptionRevision(jobId, instructionText) {
      requireSession()
      await delay(400)
      const pkg = state.packages.find((p) => p.jobId === jobId)
      if (!pkg) throw Object.assign(new Error('Package not ready yet.'), { code: 'not_ready' })
      pkg.projectDescription = `${pkg.projectDescription} (Updated: ${instructionText.trim().slice(0, 120)})`
      pkg.version += 1
      const job = getJobOrThrow(jobId)
      job.publicStatus = 'ready_for_approval'
      save()
      return structuredClone(pkg)
    },

    async getGeneratedAsset(assetId) {
      requireSession()
      await delay()
      for (const pkg of state.packages) {
        const asset = pkg.assets.find((a) => a.id === assetId)
        if (asset) return structuredClone(asset)
      }
      throw Object.assign(new Error('Content not found.'), { code: 'not_found' })
    },

    async requestAssetRevision(assetId, input: RevisionInput) {
      requireSession()
      await delay(500)
      for (const pkg of state.packages) {
        const asset = pkg.assets.find((a) => a.id === assetId)
        if (!asset) continue
        const nextVersion = asset.versions.length + 1
        const versionId = `${asset.id}-v${nextVersion}`
        const bodyExtra = input.instructionText
          ? ` (Rev: ${input.instructionText.slice(0, 80)})`
          : ' (Revised)'
        const version = {
          id: versionId,
          version: nextVersion,
          title: asset.title,
          body: asset.body + bodyExtra,
          preview: { ...asset.preview },
          sourceMediaIds: input.selectedMediaIds || asset.versions[0]?.sourceMediaIds || [],
          createdAt: new Date().toISOString(),
        }
        asset.versions.push(version)
        // Leave active on original until user selects
        const job = getJobOrThrow(pkg.jobId)
        job.publicStatus = 'ready_for_approval'
        save()
        return structuredClone(asset)
      }
      throw Object.assign(new Error('Content not found.'), { code: 'not_found' })
    },

    async selectAssetVersion(assetId, versionId) {
      requireSession()
      await delay()
      for (const pkg of state.packages) {
        const asset = pkg.assets.find((a) => a.id === assetId)
        if (!asset) continue
        const version = asset.versions.find((v) => v.id === versionId)
        if (!version) throw Object.assign(new Error('Version not found.'), { code: 'not_found' })
        asset.activeVersionId = versionId
        asset.title = version.title
        asset.body = version.body
        asset.preview = { ...version.preview }
        save()
        return structuredClone(asset)
      }
      throw Object.assign(new Error('Content not found.'), { code: 'not_found' })
    },

    async approveAndPublish(jobId, idempotencyKey) {
      requireSession()
      await delay(300)
      if (state.publishKeys.has(idempotencyKey)) {
        return structuredClone(getJobOrThrow(jobId))
      }
      const job = getJobOrThrow(jobId)
      if (job.publicStatus !== 'ready_for_approval' && job.publicStatus !== 'publish_issue') {
        throw Object.assign(new Error('This job is not ready to publish yet.'), {
          code: 'invalid_state',
        })
      }
      state.publishKeys.add(idempotencyKey)
      job.publicStatus = 'publishing'
      job.approvedAt = new Date().toISOString()
      save()
      setTimeout(() => {
        const j = state.jobs.find((x) => x.id === jobId)
        if (!j || j.publicStatus !== 'publishing') return
        j.publicStatus = 'published'
        j.publishedAt = new Date().toISOString()
        j.updatedAt = j.publishedAt
        save()
      }, 1500)
      return structuredClone(job)
    },

    async listSocialConnections() {
      requireSession()
      await delay()
      return structuredClone(state.social)
    },

    async getSocialConnectUrl() {
      requireSession()
      await delay()
      // Fake provider page: frontend route that completes return
      const url = `/settings/social-return?mock=1&status=connected`
      return {
        url,
        expiresAt: new Date(Date.now() + 10 * 60 * 1000).toISOString(),
      }
    },

    async completeSocialReturn(status = 'connected') {
      requireSession()
      await delay()
      // Mark first-ship platforms connected for the demo manage flow
      state.social = state.social.map((s) => {
        if (
          status === 'connected' &&
          (s.platform === 'facebook' ||
            s.platform === 'instagram' ||
            s.platform === 'tiktok' ||
            s.platform === 'youtube' ||
            s.platform === 'google_business')
        ) {
          return {
            ...s,
            status: 'connected' as const,
            accountName: s.accountName || `Connected ${s.platform}`,
          }
        }
        return s
      })
      save()
    },
  }

  // Dev helper on window
  if (import.meta.client) {
    ;(window as unknown as { __jobbpulseReset?: () => void }).__jobbpulseReset = () => {
      state = freshState()
      save()
      location.reload()
    }
  }

  return client
}

export function resetMockData() {
  if (import.meta.client) {
    localStorage.removeItem(STORAGE_KEY)
  }
}
