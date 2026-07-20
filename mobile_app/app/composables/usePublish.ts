/**
 * Unified publish action (Phases 6–7).
 * One Publish button — directory + optional social destinations.
 */

import type { JobDetail } from '~/composables/useJobs'

export type Publication = {
  id: string
  job_id: string
  destination_type: string
  status: string
  external_url?: string | null
  last_error?: string | null
  attempt_count?: number
  publishing_connection_id?: string | null
  provider?: string | null
  scheduled_for?: string | null
}

export type PublishResult = {
  job: JobDetail
  listing: {
    id: string
    slug: string
    status: string
    public_path: string
    public_url: string
    public_title?: string
  } | null
  publications?: Publication[]
  public_path?: string | null
  public_url?: string | null
  contractor_public_url?: string
}

export const usePublish = () => {
  const api = useApi()
  const busy = ref(false)
  const error = ref<string | null>(null)

  async function publishJob(
    jobId: string,
    opts?: {
      publishToDirectory?: boolean
      socialConnectionIds?: string[]
    },
  ): Promise<PublishResult> {
    busy.value = true
    error.value = null
    try {
      return await api.request<PublishResult>(`/api/v1/jobs/${jobId}/publish`, {
        method: 'POST',
        body: JSON.stringify({
          publish_to_directory: opts?.publishToDirectory ?? true,
          social_connection_ids: opts?.socialConnectionIds ?? [],
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

  async function listPublications(jobId: string): Promise<Publication[]> {
    const data = await api.request<{ items: Publication[] }>(
      `/api/v1/jobs/${jobId}/publications`,
    )
    return data.items || []
  }

  async function retryPublication(publicationId: string): Promise<Publication> {
    busy.value = true
    error.value = null
    try {
      return await api.request<Publication>(
        `/api/v1/publications/${publicationId}/retry`,
        { method: 'POST' },
      )
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Retry failed'
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
    listPublications,
    retryPublication,
  }
}
