import type { Job, MediaAsset, PhotoCategory, PhotoMinimums, PublicJobStatus } from '~/types/domain'

export function countsFromMedia(media: MediaAsset[]): Record<PhotoCategory, number> {
  const counts: Record<PhotoCategory, number> = { before: 0, progress: 0, after: 0 }
  for (const m of media) {
    if (m.kind !== 'photo' || m.isDeleted || m.uploadStatus !== 'complete') continue
    if (m.photoCategory) counts[m.photoCategory] += 1
  }
  return counts
}

export function meetsMinimums(
  counts: Record<PhotoCategory, number>,
  minimums: PhotoMinimums,
): boolean {
  return (
    counts.before >= minimums.before &&
    counts.progress >= minimums.progress &&
    counts.after >= minimums.after
  )
}

export function missingMinimums(
  counts: Record<PhotoCategory, number>,
  minimums: PhotoMinimums,
): PhotoCategory[] {
  const missing: PhotoCategory[] = []
  if (counts.before < minimums.before) missing.push('before')
  if (counts.progress < minimums.progress) missing.push('progress')
  if (counts.after < minimums.after) missing.push('after')
  return missing
}

export function computePublicStatus(
  counts: Record<PhotoCategory, number>,
  minimums: PhotoMinimums,
  _hasVoice: boolean,
): PublicJobStatus {
  if (meetsMinimums(counts, minimums)) return 'ready_to_finish'
  return 'active'
}

export function statusLabel(status: PublicJobStatus, job?: Job): string {
  switch (status) {
    case 'active': {
      if (job) {
        if (job.counts.after === 0 && job.counts.before > 0) return 'Needs After Photos'
        if (job.counts.before === 0) return 'Needs Before Photos'
      }
      return 'In Progress'
    }
    case 'ready_to_finish':
      return 'Ready to Finish'
    case 'processing':
      return 'Processing'
    case 'ready_for_approval':
      return 'Awaiting Approval'
    case 'needs_revision':
      return 'Needs Revision'
    case 'publishing':
      return 'Publishing'
    case 'published':
      return 'Published'
    case 'publish_issue':
      return 'Publish Issue'
    default:
      return status
  }
}

export function contextualAction(job: Job): { label: string; to: string; icon: 'camera' | 'eye' | 'check' } {
  switch (job.publicStatus) {
    case 'ready_for_approval':
    case 'needs_revision':
      return { label: 'Review Content', to: `/jobs/${job.id}/approval`, icon: 'eye' }
    case 'processing':
    case 'publishing':
      return { label: 'View Job', to: `/jobs/${job.id}`, icon: 'eye' }
    case 'published':
    case 'publish_issue':
      return { label: 'View Job', to: `/jobs/${job.id}`, icon: 'check' }
    case 'ready_to_finish':
      return { label: 'Finish Job', to: `/jobs/${job.id}/finish`, icon: 'check' }
    default: {
      const next =
        job.counts.before < 2 ? 'before' : job.counts.after < 2 ? 'after' : 'progress'
      return {
        label: 'Add Photos',
        to: `/jobs/${job.id}/photos/${next}`,
        icon: 'camera',
      }
    }
  }
}

export function categoryLabel(category: PhotoCategory): string {
  const map: Record<PhotoCategory, string> = {
    before: 'Before',
    progress: 'In-Progress',
    after: 'After',
  }
  return map[category]
}

export function destinationLabel(type: string): string {
  const map: Record<string, string> = {
    facebook: 'Facebook',
    instagram: 'Instagram',
    google_business: 'Google Business Profile',
    tiktok: 'TikTok',
    youtube: 'YouTube Shorts',
    x: 'X',
    linkedin: 'LinkedIn',
    conversion_site: 'Project Page',
    portfolio_site: 'JobbPulse Portfolio',
  }
  return map[type] || type
}

export type PreviewKind = 'facebook' | 'instagram' | 'google_business' | 'website'

export function previewKind(type: string): PreviewKind {
  if (type === 'facebook' || type === 'instagram' || type === 'google_business') {
    return type
  }
  return 'website'
}
