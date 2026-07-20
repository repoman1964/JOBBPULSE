/**
 * Jobs list + create helpers.
 *
 * `title` is the contractor's private job name (required). It is never for
 * AI generation, social, or the public directory.
 */

export type NextAction = {
  action: string
  label: string
  cta: string
  reason: string
  optional_tip?: string | null
}

export type PhotoCounts = {
  total: number
  before: number
  after: number
  has_before_after_pair: boolean
}

export type TimelineStep = {
  key: string
  label: string
  status: 'complete' | 'current' | 'upcoming' | 'locked' | 'optional' | 'skipped' | string
}

/** Private contractor label — do not send to marketing/AI surfaces. */
export type JobSummary = {
  id: string
  title: string
  service_key?: string | null
  location_display?: string | null
  city?: string | null
  state?: string | null
  status: string
  photo_counts: PhotoCounts
  next_action: NextAction
  timeline: TimelineStep[]
  created_at: string
  updated_at: string
}

export type MediaAsset = {
  id: string
  job_id: string
  storage_key: string
  url?: string | null
  original_filename?: string | null
  mime_type?: string | null
  file_size_bytes?: number | null
  stage_label: 'before' | 'after' | string
  display_order: number
  is_primary: boolean
  processing_status: string
  created_at: string
}

export type JobDetail = JobSummary & {
  company_id: string
  created_by?: string | null
  postal_code?: string | null
  customer_name_private?: string | null
  customer_consent_status: string
  notes?: string | null
  privacy_mode: string
  media: MediaAsset[]
  job_started_at?: string | null
  job_completed_at?: string | null
}

export function statusLabel(status: string): string {
  const map: Record<string, string> = {
    draft: 'Draft',
    before_photos_added: 'Before photos added',
    work_in_progress: 'In progress',
    ready_for_summary: 'Ready for summary',
    ready_to_generate: 'Ready to generate',
    generating: 'Generating',
    awaiting_review: 'Needs review',
    revision_requested: 'Revision requested',
    approved: 'Approved',
    scheduled: 'Scheduled',
    published: 'Published',
    failed: 'Failed',
    archived: 'Archived',
  }
  return map[status] || status
}

export function isIncompleteJob(job: JobSummary): boolean {
  return !['published', 'archived', 'approved', 'scheduled'].includes(job.status)
}

export const useJobs = () => {
  const api = useApi()
  const jobs = useState<JobSummary[]>('jobs.list', () => [])
  const loading = useState<boolean>('jobs.loading', () => false)
  const error = useState<string | null>('jobs.error', () => null)

  const incompleteJobs = computed(() => jobs.value.filter(isIncompleteJob))
  const resumeJob = computed(() => incompleteJobs.value[0] || null)

  async function fetchJobs() {
    loading.value = true
    error.value = null
    try {
      jobs.value = (await api.listJobs()) as JobSummary[]
    } catch (e: any) {
      error.value = e?.message || 'Failed to load jobs'
      throw e
    } finally {
      loading.value = false
    }
  }

  async function createJob(payload: Record<string, unknown>) {
    if (!payload.title || !String(payload.title).trim()) {
      throw new Error('Job name is required.')
    }
    const job = (await api.createJob(payload)) as JobDetail
    await fetchJobs().catch(() => undefined)
    return job
  }

  return {
    jobs,
    loading,
    error,
    incompleteJobs,
    resumeJob,
    fetchJobs,
    createJob,
    statusLabel,
  }
}
