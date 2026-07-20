/**
 * Content review / approve helpers (Phase 5).
 * Contractor edits drafts; manager+ approve/reject.
 */

import type { ContentVariant } from '~/composables/useGeneration'
import type { JobDetail } from '~/composables/useJobs'

export type ContentVariantDetail = ContentVariant & {
  body_effective?: string
  approved_by?: string | null
  approved_at?: string | null
  rejected_at?: string | null
}

export type ApprovalReadiness = {
  can_approve_job: boolean
  blockers: string[]
  soft_warnings: string[]
  social_approved: boolean
  directory_approved: boolean
  after_count: number
  before_count: number
}

export type ApproveJobResult = {
  job: JobDetail
  variants: ContentVariantDetail[]
  readiness: ApprovalReadiness
}

export const useContentReview = () => {
  const api = useApi()
  const busy = useState<boolean>('contentReview.busy', () => false)
  const error = useState<string | null>('contentReview.error', () => null)

  async function getVariant(contentId: string): Promise<ContentVariantDetail> {
    return (await api.request(`/api/v1/content/${contentId}`)) as ContentVariantDetail
  }

  async function updateVariant(
    contentId: string,
    payload: {
      body_edited?: string | null
      title?: string | null
      call_to_action?: string | null
      hashtags_json?: string[] | null
    },
  ): Promise<ContentVariantDetail> {
    busy.value = true
    error.value = null
    try {
      return (await api.request(`/api/v1/content/${contentId}`, {
        method: 'PATCH',
        body: JSON.stringify(payload),
      })) as ContentVariantDetail
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Save failed'
      throw e
    } finally {
      busy.value = false
    }
  }

  async function approveVariant(contentId: string): Promise<ContentVariantDetail> {
    busy.value = true
    error.value = null
    try {
      return (await api.request(`/api/v1/content/${contentId}/approve`, {
        method: 'POST',
      })) as ContentVariantDetail
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Approve failed'
      throw e
    } finally {
      busy.value = false
    }
  }

  async function rejectVariant(
    contentId: string,
    reason?: string,
  ): Promise<ContentVariantDetail> {
    busy.value = true
    error.value = null
    try {
      return (await api.request(`/api/v1/content/${contentId}/reject`, {
        method: 'POST',
        body: JSON.stringify({ reason: reason || null }),
      })) as ContentVariantDetail
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Reject failed'
      throw e
    } finally {
      busy.value = false
    }
  }

  async function getReadiness(jobId: string): Promise<ApprovalReadiness> {
    return (await api.request(
      `/api/v1/jobs/${jobId}/approval-readiness`,
    )) as ApprovalReadiness
  }

  async function approveAll(jobId: string): Promise<ApproveJobResult> {
    busy.value = true
    error.value = null
    try {
      return (await api.request(`/api/v1/jobs/${jobId}/approve-all`, {
        method: 'POST',
      })) as ApproveJobResult
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Approve all failed'
      throw e
    } finally {
      busy.value = false
    }
  }

  async function approveJob(jobId: string): Promise<ApproveJobResult> {
    busy.value = true
    error.value = null
    try {
      return (await api.request(`/api/v1/jobs/${jobId}/approve`, {
        method: 'POST',
      })) as ApproveJobResult
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Job approve failed'
      throw e
    } finally {
      busy.value = false
    }
  }

  return {
    busy,
    error,
    getVariant,
    updateVariant,
    approveVariant,
    rejectVariant,
    getReadiness,
    approveAll,
    approveJob,
  }
}
