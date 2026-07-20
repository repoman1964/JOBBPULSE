/**
 * AI content generation helpers (Phase 4).
 * Review / approve lives in useContentReview (Phase 5).
 */

import type { JobDetail } from '~/composables/useJobs'

export type ContentVariant = {
  id: string
  job_id: string
  generation_run_id: string
  content_type: string
  platform_target?: string | null
  title?: string | null
  body_generated: string
  body_edited?: string | null
  call_to_action?: string | null
  hashtags_json?: string[] | null
  status: string
  version_number: number
  created_at: string
  updated_at: string
}

export type GenerationRun = {
  id: string
  job_id: string
  status: string
  generation_type: string
  tone?: string | null
  length_preference?: string | null
  user_instruction?: string | null
  model_provider?: string | null
  model_name?: string | null
  prompt_version?: string | null
  input_snapshot_json?: Record<string, unknown> | null
  output_snapshot_json?: Record<string, unknown> | null
  error_message?: string | null
  completed_at?: string | null
  created_at: string
  updated_at: string
  variants: ContentVariant[]
  warnings: string[]
}

export type JobContent = {
  job_id: string
  structured_details?: Record<string, unknown> | null
  variants: ContentVariant[]
  latest_generation_run_id?: string | null
  generation_version: number
}

export type GenerateResult = {
  run: GenerationRun
  job: JobDetail
  variants: ContentVariant[]
  warnings: string[]
}

const CONTENT_TYPE_LABELS: Record<string, string> = {
  primary_social: 'Primary social post',
  short_caption: 'Short caption',
  before_after: 'Before & after',
  directory_listing: 'Directory listing',
  educational: 'Educational',
}

export function contentTypeLabel(type: string): string {
  return CONTENT_TYPE_LABELS[type] || type
}

export const useGeneration = () => {
  const api = useApi()
  const generating = useState<boolean>('generation.busy', () => false)
  const error = useState<string | null>('generation.error', () => null)

  async function generate(
    jobId: string,
    payload: {
      tone?: string
      length_preference?: string
      user_instruction?: string
    } = {},
  ): Promise<GenerateResult> {
    generating.value = true
    error.value = null
    try {
      return (await api.request(`/api/v1/jobs/${jobId}/generate`, {
        method: 'POST',
        body: JSON.stringify(payload),
      })) as GenerateResult
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Generation failed'
      throw e
    } finally {
      generating.value = false
    }
  }

  async function regenerate(
    jobId: string,
    payload: {
      tone?: string
      length_preference?: string
      user_instruction?: string
    } = {},
  ): Promise<GenerateResult> {
    generating.value = true
    error.value = null
    try {
      return (await api.request(`/api/v1/jobs/${jobId}/regenerate`, {
        method: 'POST',
        body: JSON.stringify(payload),
      })) as GenerateResult
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Regeneration failed'
      throw e
    } finally {
      generating.value = false
    }
  }

  async function getContent(jobId: string): Promise<JobContent> {
    return (await api.request(`/api/v1/jobs/${jobId}/content`)) as JobContent
  }

  async function getRun(runId: string): Promise<GenerationRun> {
    return (await api.request(`/api/v1/generation-runs/${runId}`)) as GenerationRun
  }

  return {
    generating,
    error,
    generate,
    regenerate,
    getContent,
    getRun,
    contentTypeLabel,
  }
}
