export type CarouselJob = {
  slug: string
  publicTitle: string
  publicSummary: string
  serviceType: string
  city: string
  publishedAt?: string | null
  primaryImageUrl?: string | null
  hasBefore: boolean
  hasAfter: boolean
}

export function mergeLiveAndDummy(live: CarouselJob[], dummy: CarouselJob[]): CarouselJob[] {
  const seen = new Set<string>()
  const out: CarouselJob[] = []
  for (const item of [...live, ...dummy]) {
    if (!item.slug || seen.has(item.slug)) continue
    seen.add(item.slug)
    out.push(item)
  }
  return out
}

function asRecord(value: unknown): Record<string, unknown> | null {
  return value && typeof value === 'object' && !Array.isArray(value) ? (value as Record<string, unknown>) : null
}

function mapCarouselJob(raw: Record<string, unknown>): CarouselJob | null {
  const slug = String(raw.slug || '')
  if (!slug) return null
  return {
    slug,
    publicTitle: String(raw.publicTitle || raw.public_title || ''),
    publicSummary: String(raw.publicSummary || raw.public_summary || raw.short_summary || ''),
    serviceType: String(raw.serviceType || raw.service_type || raw.service_name || ''),
    city: String(raw.city || raw.location_display || ''),
    publishedAt: (raw.publishedAt as string) || (raw.published_at as string) || null,
    primaryImageUrl: (raw.primaryImageUrl as string) || (raw.primary_image_url as string) || null,
    hasBefore: Boolean(raw.hasBefore ?? raw.has_before),
    hasAfter: Boolean(raw.hasAfter ?? raw.has_after),
  }
}

export function parseDemoListPayload(payload: unknown): CarouselJob[] {
  const root = asRecord(payload)
  const data = asRecord(root?.data)
  const rawItems = data?.items ?? root?.items ?? (Array.isArray(root?.data) ? root?.data : null) ?? root?.data
  const list = Array.isArray(rawItems) ? rawItems : []
  const jobs: CarouselJob[] = []
  for (const item of list) {
    const rec = asRecord(item)
    if (!rec) continue
    const job = mapCarouselJob(rec)
    if (job) jobs.push(job)
  }
  return jobs
}

export function isDummySlug(slug: string): boolean {
  return slug.startsWith('demo-')
}

export function publicChromeHasForbiddenWords(text: string): boolean {
  return /\bjobbpulse\b|\bjobpulse\b/i.test(text)
}
