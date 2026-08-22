export type ProjectCard = {
  id: string
  slug: string
  public_title: string
  short_summary?: string
  service_key?: string | null
  service_name?: string
  service_slug?: string
  location_display?: string | null
  city?: string | null
  state?: string | null
  location_slug?: string | null
  featured?: boolean
  published_at?: string | null
  public_path: string
  primary_image_url?: string | null
  has_before?: boolean
  has_after?: boolean
  has_before_after?: boolean
  media_count?: number
  contractor?: {
    slug?: string | null
    company_name?: string | null
    public_path?: string | null
    portfolio_path?: string | null
  }
}

export type MediaItem = {
  id: string
  stage_label: string
  display_order: number
  url?: string | null
}

export type ProjectDetail = ProjectCard & {
  public_summary: string
  seo_title?: string | null
  seo_description?: string | null
  media: MediaItem[]
  contractor: {
    slug?: string | null
    company_name?: string | null
    headline?: string | null
    public_path?: string | null
    about_path?: string | null
    portfolio_path?: string | null
    trade?: string | null
    contact_phone?: string | null
    website_url?: string | null
    lead_form_enabled?: boolean
    public_description?: string | null
  }
  related?: {
    same_contractor?: ProjectCard[]
    same_city?: ProjectCard[]
    same_service?: ProjectCard[]
    nearby?: ProjectCard[]
  }
}

export type Contractor = {
  id: string
  slug: string
  company_name: string
  headline?: string | null
  public_description?: string | null
  trade?: string | null
  contact_phone?: string | null
  website_url?: string | null
  lead_form_enabled?: boolean
  featured?: boolean
  project_count?: number
  public_path: string
  about_path?: string
  portfolio_path?: string
  services?: { service_key: string; display_name: string; slug?: string }[]
  service_areas?: { city?: string; state?: string; display_name: string; slug?: string | null }[]
  recent_projects?: ProjectCard[]
  primary_city?: string | null
  primary_state?: string | null
  seo_title?: string | null
  seo_description?: string | null
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

export function usePublicApi() {
  return {
    getHome: () =>
      publicGet<{
        recent_projects: ProjectCard[]
        featured_projects: ProjectCard[]
        featured_contractors: Contractor[]
        popular_services: { slug: string; name: string; project_count: number; public_path: string }[]
        popular_locations: { slug: string; name: string; project_count: number; public_path: string }[]
      }>('/home'),

    listProjects: (query?: Record<string, string | number | boolean | undefined | null>) =>
      publicGet<{ items: ProjectCard[]; limit: number; offset: number }>('/projects', query),

    getProject: (slug: string) => publicGet<ProjectDetail>(`/projects/${encodeURIComponent(slug)}`),

    listContractors: (query?: Record<string, string | number | boolean | undefined | null>) =>
      publicGet<{ items: Contractor[] }>('/contractors', query),

    getContractor: (slug: string, query?: Record<string, string | number | boolean | undefined | null>) =>
      publicGet<Contractor>(`/contractors/${encodeURIComponent(slug)}`, query),

    listServices: () =>
      publicGet<{ items: { slug: string; name: string; description?: string; project_count: number; public_path: string; service_key: string }[] }>(
        '/services',
      ),

    getService: (slug: string) =>
      publicGet<{
        slug: string
        name: string
        description?: string
        project_count: number
        projects: ProjectCard[]
        contractors: Contractor[]
        locations: { slug: string; city: string; state?: string; project_count: number; public_path: string }[]
      }>(`/services/${encodeURIComponent(slug)}`),

    listLocations: () =>
      publicGet<{ items: { slug: string; name: string; city: string; state?: string; project_count: number; public_path: string }[] }>(
        '/locations',
      ),

    getLocation: (slug: string) =>
      publicGet<{
        slug: string
        name: string
        city: string
        state?: string
        project_count: number
        projects: ProjectCard[]
        contractors: Contractor[]
        services: { slug: string; name: string; project_count: number; public_path: string }[]
      }>(`/locations/${encodeURIComponent(slug)}`),

    getLocationService: (locationSlug: string, serviceSlug: string) =>
      publicGet<{
        title: string
        project_count: number
        projects: ProjectCard[]
        contractors: Contractor[]
        location: { slug: string; name: string; city?: string; public_path: string }
        service: { slug: string; name: string; public_path: string }
      }>(`/locations/${encodeURIComponent(locationSlug)}/${encodeURIComponent(serviceSlug)}`),

    search: (query?: Record<string, string | number | boolean | undefined | null>) =>
      publicGet<{ query?: string; projects: ProjectCard[]; contractors: Contractor[] }>('/search', query),

    createLead: (body: {
      contractor_slug: string
      name: string
      email?: string
      phone?: string
      message?: string
      project_slug?: string
      project_location?: string
      service_requested?: string
      preferred_contact_method?: string
      source_page_type?: string
      source_page_url?: string
    }) => publicPost<{ ok: boolean; id?: string; message: string }>('/leads', body),
  }
}
