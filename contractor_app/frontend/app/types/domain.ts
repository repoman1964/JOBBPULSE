/** Domain types aligned with future /api/v1 backend shapes. */

export type PhotoCategory = 'before' | 'progress' | 'after'

export type PublicJobStatus =
  | 'active'
  | 'ready_to_finish'
  | 'processing'
  | 'ready_for_approval'
  | 'needs_revision'
  | 'publishing'
  | 'published'
  | 'publish_issue'

export type InternalJobStatus =
  | 'draft'
  | 'submitted'
  | 'queued'
  | 'transcribing'
  | 'curating_media'
  | 'generating'
  | 'generating_description'
  | 'generating_destinations'
  | 'ready_for_approval'
  | 'revision_requested'
  | 'regenerating'
  | 'approved'
  | 'publishing'
  | 'published'
  | 'partially_failed'
  | 'failed'

export type SocialPlatform = 'facebook' | 'instagram' | 'google_business'

export type SocialConnectionStatus =
  | 'connected'
  | 'not_connected'
  | 'reconnect_required'
  | 'connection_pending'
  | 'provider_unavailable'

export type DestinationType =
  | 'facebook'
  | 'facebook_group'
  | 'instagram'
  | 'google_business'
  | 'tiktok'
  | 'youtube'
  | 'x'
  | 'linkedin'
  | 'conversion_site'
  | 'portfolio_site'

export type UploadStatus = 'pending' | 'uploading' | 'complete' | 'failed'

export interface PhotoMinimums {
  before: number
  progress: number
  after: number
}

export interface PhotoMaximums {
  before: number
  progress: number
  after: number
}

export interface NotificationSettings {
  contentReadyForApproval: boolean
  publishingComplete: boolean
}

export interface Company {
  id: string
  name: string
  contactName: string
  phone: string
  email: string
  website: string
  serviceArea: string
  photoMinimums: PhotoMinimums
  photoMaximums: PhotoMaximums
  notificationSettings: NotificationSettings
}

export interface Contractor {
  id: string
  companyId: string
  name: string
  email: string
  phone: string
  role: string
}

export interface Session {
  accessToken: string
  contractor: Contractor
  company: Company
}

export interface Job {
  id: string
  companyId: string
  name: string
  serviceType: string
  city: string
  region: string
  locationText: string
  internalNote: string
  assignedCrewMember: string
  publicStatus: PublicJobStatus
  internalStatus?: InternalJobStatus | string
  coverUrl: string | null
  counts: Record<PhotoCategory, number>
  hasVoice: boolean
  createdAt: string
  updatedAt: string
  submittedAt: string | null
  approvedAt: string | null
  publishedAt: string | null
  deletedAt?: string | null
}

export interface MediaAsset {
  id: string
  jobId: string
  kind: 'photo' | 'audio'
  photoCategory: PhotoCategory | null
  url: string
  thumbnailUrl: string
  mimeType: string
  byteSize: number
  durationMs: number | null
  uploadStatus: UploadStatus
  isFavorite: boolean
  isDeleted: boolean
  version: number
  createdAt: string
}

export interface UploadSession {
  mediaId: string
  uploadUrl: string
  expiresAt: string
}

export interface GeneratedAssetVersion {
  id: string
  version: number
  title: string
  body: string
  preview: Record<string, unknown>
  sourceMediaIds: string[]
  createdAt: string
}

export interface GeneratedAsset {
  id: string
  packageId: string
  destinationType: DestinationType
  title: string
  body: string
  status: string
  activeVersionId: string
  versions: GeneratedAssetVersion[]
  preview: Record<string, unknown>
}

export interface ContentPackage {
  id: string
  jobId: string
  version: number
  status: string
  projectDescription: string
  featuredBeforeMediaId: string | null
  featuredAfterMediaId: string | null
  assets: GeneratedAsset[]
}

export interface SocialConnection {
  platform: SocialPlatform
  status: SocialConnectionStatus
  accountName: string | null
  reason: string | null
}

export interface CreateJobInput {
  name: string
  serviceType: string
  city: string
  region?: string
  locationText?: string
  internalNote?: string
  assignedCrewMember?: string
}

export interface UpdateCompanyInput {
  name?: string
  contactName?: string
  phone?: string
  email?: string
  website?: string
  serviceArea?: string
}

export interface ApiError {
  code: string
  message: string
  fieldErrors?: Record<string, string>
}
