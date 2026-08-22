/** Public JobPulse directory API client for Red Clay's Smart Website. */

export type ProjectCard = {
  id: string
  slug: string
  public_title: string
  short_summary?: string
  public_summary?: string
  service_key?: string | null
  service_name?: string
  location_display?: string | null
  city?: string | null
  state?: string | null
  featured?: boolean
  published_at?: string | null
  public_path?: string
  public_url?: string
  primary_image_url?: string | null
  has_before?: boolean
  has_after?: boolean
  media_count?: number
}

export type MediaItem = {
  id: string
  stage_label: string
  display_order: number
  url?: string | null
}

export type ProjectDetail = ProjectCard & {
  public_summary: string
  media: MediaItem[]
  contractor?: {
    slug?: string | null
    company_name?: string | null
    contact_phone?: string | null
  }
}

export type ContractorProfile = {
  id: string
  slug: string
  company_name: string
  headline?: string | null
  public_description?: string | null
  trade?: string | null
  contact_phone?: string | null
  project_count?: number
  recent_projects?: ProjectCard[]
  services?: { service_key: string; display_name: string; slug?: string }[]
  service_areas?: { city?: string; state?: string; display_name: string }[]
}

type ApiEnvelope<T> = {
  success?: boolean
  data: T
  error?: { code?: string; message?: string }
}

function apiBase() {
  const config = useRuntimeConfig()
  return String(config.public.apiBase || 'http://localhost:8000').replace(/\/$/, '')
}

function contractorSlug() {
  const config = useRuntimeConfig()
  return String(config.public.contractorSlug || 'red-clay-cabinet-installers')
}

async function publicGet<T>(path: string, query?: Record<string, string | number | boolean | undefined | null>) {
  const base = apiBase()
  const qs = new URLSearchParams()
  if (query) {
    for (const [k, v] of Object.entries(query)) {
      if (v === undefined || v === null || v === '') continue
      qs.set(k, String(v))
    }
  }
  const url = `${base}/api/v1/public${path}${qs.toString() ? `?${qs}` : ''}`
  const res = await $fetch<ApiEnvelope<T>>(url)
  return res.data
}

async function publicPost<T>(path: string, body: Record<string, unknown>) {
  const base = apiBase()
  const res = await $fetch<ApiEnvelope<T>>(`${base}/api/v1/public${path}`, {
    method: 'POST',
    body,
  })
  return res.data
}

export function useJobPulse() {
  const slug = contractorSlug()

  return {
    contractorSlug: slug,

    getContractor: (projectLimit = 12) =>
      publicGet<ContractorProfile>(`/contractors/${encodeURIComponent(slug)}`, {
        project_limit: projectLimit,
      }),

    listProjects: (limit = 12, offset = 0) =>
      publicGet<{ items: ProjectCard[]; limit: number; offset: number }>('/projects', {
        contractor_slug: slug,
        limit,
        offset,
      }),

    getProject: (projectSlug: string) =>
      publicGet<ProjectDetail>(`/projects/${encodeURIComponent(projectSlug)}`),

    createLead: (body: {
      name: string
      email?: string
      phone?: string
      message?: string
      service_requested?: string
      project_location?: string
      preferred_contact_method?: string
      source_page_type?: string
      source_page_url?: string
    }) =>
      publicPost('/leads', {
        contractor_slug: slug,
        ...body,
      }),
  }
}
