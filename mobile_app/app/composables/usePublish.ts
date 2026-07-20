/**
 * Unified publish action (Phase 6).
 * One Publish button — directory now; social destinations later on the same path.
 */

import type { JobDetail } from '~/composables/useJobs'

export type PublishResult = {
  job: JobDetail
  listing: {
    id: string
    slug: string
    status: string
    public_path: string
    public_url: string
    public_title?: string
  }
  public_path: string
  public_url: string
  contractor_public_url?: string
}

export const usePublish = () => {
  const api = useApi()
  const busy = ref(false)
  const error = ref<string | null>(null)

  async function publishJob(jobId: string): Promise<PublishResult> {
    busy.value = true
    error.value = null
    try {
      return await api.request<PublishResult>(`/api/v1/jobs/${jobId}/publish`, {
        method: 'POST',
        body: JSON.stringify({
          publish_to_directory: true,
          social_connection_ids: [],
        }),
      })
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Publish failed'
      throw e
    } finally {
      busy.value = false
    }
  }

  async function unpublishJob(jobId: string) {
    busy.value = true
    error.value = null
    try {
      return await api.request(`/api/v1/jobs/${jobId}/unpublish-directory`, {
        method: 'POST',
      })
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Unpublish failed'
      throw e
    } finally {
      busy.value = false
    }
  }

  return {
    busy,
    error,
    publishJob,
    unpublishJob,
  }
}
