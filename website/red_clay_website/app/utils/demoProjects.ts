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

export function isDummySlug(slug: string): boolean {
  return slug.startsWith('demo-')
}

export function publicChromeHasForbiddenWords(text: string): boolean {
  return /\bjobbpulse\b|\bjobpulse\b/i.test(text)
}
