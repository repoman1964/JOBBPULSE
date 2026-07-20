/**
 * Public directory API client (no auth).
 */

type ApiEnvelope<T> = {
  data: T
  meta: Record<string, unknown>
  error: null | { code: string; message: string; details?: Record<string, unknown> }
}

export type PublicMedia = {
  id: string
  stage_label: string
  display_order: number
  url: string | null
  mime_type?: string | null
  width?: number | null
  height?: number | null
}

export type PublicProject = {
  id: string
  slug: string
  public_title: string
  public_summary: string
  service_key: string | null
  location_display: string | null
  city: string | null
  state: string | null
  status: string
  published_at: string | null
  seo_title: string | null
  seo_description: string | null
  structured_data_json?: Record<string, unknown> | null
  public_path: string
  public_url: string
  media: PublicMedia[]
  contractor: {
    slug: string | null
    headline: string | null
    company_name: string | null
    public_path: string | null
    public_url: string | null
    trade: string | null
  }
}

export type PublicContractor = {
  id: string
  slug: string
  headline: string | null
  public_description: string | null
  company_name: string
  trade: string | null
  contact_phone: string | null
  website_url: string | null
  lead_form_enabled: boolean
  seo_title: string | null
  seo_description: string | null
  public_path: string
  public_url: string
  services: { service_key: string; display_name: string }[]
  service_areas: {
    city: string | null
    state: string | null
    display_name: string
    is_primary: boolean
  }[]
  recent_projects: {
    slug: string
    public_title: string
    service_key: string | null
    city: string | null
    state: string | null
    location_display: string | null
    published_at: string | null
    public_path: string
    public_url: string
  }[]
}

export const usePublicApi = () => {
  const config = useRuntimeConfig()
  const base = config.public.apiBase as string

  async function get<T>(path: string): Promise<T> {
    const res = await $fetch<ApiEnvelope<T>>(`${base}${path}`)
    if (res.error) {
      throw createError({
        statusCode: 404,
        statusMessage: res.error.message || 'Not found',
      })
    }
    return res.data
  }

  return {
    listProjects: (params?: { limit?: number }) => {
      const q = new URLSearchParams()
      if (params?.limit) q.set('limit', String(params.limit))
      const qs = q.toString()
      return get<{ items: PublicProject[] }>(`/api/v1/public/projects${qs ? `?${qs}` : ''}`)
    },
    getProject: (slug: string) => get<PublicProject>(`/api/v1/public/projects/${encodeURIComponent(slug)}`),
    getContractor: (slug: string) =>
      get<PublicContractor>(`/api/v1/public/contractors/${encodeURIComponent(slug)}`),
    listContractors: (params?: { limit?: number }) => {
      const q = new URLSearchParams()
      if (params?.limit) q.set('limit', String(params.limit))
      const qs = q.toString()
      return get<{ items: PublicContractor[] }>(
        `/api/v1/public/contractors${qs ? `?${qs}` : ''}`,
      )
    },
  }
}
