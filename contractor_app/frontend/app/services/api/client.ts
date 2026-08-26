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

export interface ListJobsParams {
  status?: string
  cursor?: string
}

export interface ListJobsResult {
  items: Job[]
  nextCursor: string | null
}

export interface SubmitJobInput {
  idempotencyKey: string
}

export interface RevisionInput {
  changeType: 'photos' | 'wording' | 'other'
  instructionText?: string
  selectedMediaIds?: string[]
}

/**
 * Backend-ready port. Screens must use this interface only.
 * MockApiClient implements it today; HttpApiClient will call /api/v1 later.
 */
export interface ApiClient {
  // Auth
  register(input: {
    name: string
    email: string
    password: string
    companyName: string
    phone?: string
  }): Promise<{
    email: string
    companyId: string
    contractorId: string
    verificationUrl?: string
  }>
  login(email: string, password: string): Promise<Session>
  verifyEmail(token: string): Promise<{ email: string; verified: boolean }>
  resendVerification(email: string): Promise<void>
  logout(): Promise<void>
  getSession(): Promise<Session | null>

  // Company
  getCompany(): Promise<Company>
  updateCompany(input: UpdateCompanyInput): Promise<Company>
  updateNotificationSettings(
    settings: Company['notificationSettings'],
  ): Promise<Company>

  // Jobs
  listJobs(params?: ListJobsParams): Promise<ListJobsResult>
  getJob(jobId: string): Promise<Job>
  createJob(input: CreateJobInput): Promise<Job>
  updateJob(jobId: string, input: Partial<CreateJobInput>): Promise<Job>
  deleteJob(jobId: string): Promise<void>
  submitJob(jobId: string, input: SubmitJobInput): Promise<Job>

  // Media
  createPhotoUploadSession(
    jobId: string,
    category: PhotoCategory,
    meta: { mimeType: string; byteSize: number; filename?: string },
  ): Promise<UploadSession>
  completeMediaUpload(jobId: string, mediaId: string, localObjectUrl?: string): Promise<MediaAsset>
  createVoiceUploadSession(
    jobId: string,
    meta: { mimeType: string; byteSize: number; durationMs: number },
  ): Promise<UploadSession>
  completeVoiceUpload(jobId: string, mediaId: string, localObjectUrl?: string): Promise<MediaAsset>
  /** Active voice note for a job, if any */
  getVoice(jobId: string): Promise<MediaAsset | null>
  listMedia(jobId: string, category?: PhotoCategory): Promise<MediaAsset[]>
  updateMedia(
    jobId: string,
    mediaId: string,
    patch: { isFavorite?: boolean; photoCategory?: PhotoCategory },
  ): Promise<MediaAsset>
  deleteMedia(jobId: string, mediaId: string): Promise<void>

  // Package / revisions
  getPackage(jobId: string): Promise<ContentPackage | null>
  updateFeaturedMedia(
    jobId: string,
    featuredBeforeMediaId: string,
    featuredAfterMediaId: string,
  ): Promise<ContentPackage>
  requestDescriptionRevision(jobId: string, instructionText: string): Promise<ContentPackage>
  getGeneratedAsset(assetId: string): Promise<GeneratedAsset>
  requestAssetRevision(assetId: string, input: RevisionInput): Promise<GeneratedAsset>
  selectAssetVersion(assetId: string, versionId: string): Promise<GeneratedAsset>
  approveAndPublish(jobId: string, idempotencyKey: string): Promise<Job>

  // Social
  listSocialConnections(): Promise<SocialConnection[]>
  connectSocialAccount(platform: SocialPlatform, accountName: string): Promise<SocialConnection>
  disconnectSocialAccount(platform: SocialPlatform): Promise<SocialConnection>
  getSocialConnectUrl(): Promise<{ url: string; expiresAt: string }>
  /** Mock-only helper: complete fake connect return */
  completeSocialReturn?(status?: string): Promise<void>
}
