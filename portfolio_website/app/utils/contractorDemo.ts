/**
 * Demo-only trust chips and review cards for contractor profile mockup fidelity.
 * Not backed by API fields — stable per slug so demos look consistent.
 */

export type DemoTrustChip = { label: string }

export type DemoReview = {
  author: string
  rating: number
  date: string
  text: string
  source?: string
}

const DEFAULT_CHIPS: DemoTrustChip[] = [
  { label: '12 Years in Business' },
  { label: 'Licensed & Insured' },
  { label: 'Family Owned' },
  { label: 'Responds in ~2 hrs' },
]

const DEFAULT_REVIEWS: DemoReview[] = [
  {
    author: 'Michael T.',
    rating: 5,
    date: 'Oct 12, 2023',
    text: 'Absolutely incredible work on our backyard. Highly recommend.',
    source: 'Google',
  },
  {
    author: 'Sarah Jenkins',
    rating: 5,
    date: 'Nov 5, 2023',
    text: 'Professional, on time, and left our property spotless.',
    source: 'Google',
  },
  {
    author: 'David Chen',
    rating: 5,
    date: 'Dec 1, 2023',
    text: 'The finished project is a work of art. Thank you!',
    source: 'Google',
  },
]

/** Lightweight hash so demo content varies slightly by contractor. */
function hashSlug(slug: string): number {
  let h = 0
  for (let i = 0; i < slug.length; i++) h = (h * 31 + slug.charCodeAt(i)) >>> 0
  return h
}

const RED_CLAY_SLUG = 'red-clay-cabinet-installers'

const RED_CLAY_CHIPS: DemoTrustChip[] = [
  { label: '12 Years in Business' },
  { label: 'Licensed & Insured' },
  { label: 'Serving Metro Atlanta' },
  { label: 'Free Estimates' },
]

const RED_CLAY_REVIEWS: DemoReview[] = [
  {
    author: 'Priya M.',
    rating: 5,
    date: 'Mar 3, 2026',
    text: 'Kitchen looks magazine-ready. Crew was careful with our floors.',
    source: 'Google',
  },
  {
    author: 'Tom R.',
    rating: 5,
    date: 'Feb 18, 2026',
    text: 'Vanity and mirror install same day. Explained every step.',
    source: 'Google',
  },
  {
    author: 'Elena V.',
    rating: 5,
    date: 'Jan 22, 2026',
    text: 'Pantry built-in solved our chaos. On time and tidy.',
    source: 'Google',
  },
]

export function demoTrustChips(slug: string, trade?: string | null): DemoTrustChip[] {
  if (slug === RED_CLAY_SLUG) return RED_CLAY_CHIPS

  const h = hashSlug(slug || 'x')
  const years = 8 + (h % 15)
  const areaChips = [
    { label: 'Serving North Atlanta' },
    { label: 'Serving Metro Atlanta' },
    { label: 'Local & Family Owned' },
  ]
  const chips: DemoTrustChip[] = [
    { label: `${years} Years in Business` },
    { label: 'Licensed & Insured' },
    areaChips[h % areaChips.length],
    { label: h % 2 === 0 ? 'Responds in ~2 hrs' : 'Free Estimates' },
  ]
  if (trade) {
    chips[2] = { label: trade.length > 28 ? trade.slice(0, 26) + '…' : trade }
  }
  return chips.length ? chips : DEFAULT_CHIPS
}

export function demoReviews(slug: string): DemoReview[] {
  if (slug === RED_CLAY_SLUG) return RED_CLAY_REVIEWS

  const h = hashSlug(slug || 'x')
  // Rotate default set so different contractors don't look identical
  const n = DEFAULT_REVIEWS.length
  const start = h % n
  return [...DEFAULT_REVIEWS.slice(start), ...DEFAULT_REVIEWS.slice(0, start)]
}

export function demoRatingSummary(slug: string): { rating: number; count: number } {
  if (slug === RED_CLAY_SLUG) return { rating: 4.9, count: 18 }

  const h = hashSlug(slug || 'x')
  return {
    rating: 4.7 + (h % 4) * 0.1,
    count: 48 + (h % 90),
  }
}

/**
 * Demo blurb for a contractor service tab when the API has no per-service copy.
 * Stable per slug + service so the profile mockup stays consistent.
 */
export function demoServiceBlurb(
  companyName: string,
  serviceName: string,
  slug?: string | null,
  areaLabel?: string | null,
): string {
  const name = (companyName || 'Our team').trim()
  const service = (serviceName || 'this service').trim()
  const serviceLower = service.toLowerCase()
  const area = (areaLabel || '').trim()
  const h = hashSlug(`${slug || 'x'}|${serviceName || ''}`)

  const openers = [
    `${name} provides professional ${serviceLower} for homeowners who want reliable craftsmanship and clear communication.`,
    `Looking for quality ${serviceLower}? ${name} delivers dependable results from the first visit through final walkthrough.`,
    `${name} specializes in ${serviceLower}, with careful prep, clean job sites, and finishes built to last.`,
  ]
  const middles = [
    area
      ? `We regularly serve clients in ${area}, tailoring each project to the property and budget.`
      : `We tailor each project to your property, timeline, and budget.`,
    area
      ? `Homeowners across ${area} trust us for thorough workmanship and straightforward estimates.`
      : `Every job starts with a clear plan and a straightforward estimate.`,
    `Our crew focuses on the details that matter—prep, materials, and a polished finish.`,
  ]
  const closers = [
    `Tell us about your project and we’ll outline the best approach for your ${serviceLower} needs.`,
    `Request an estimate to see how we can help with your next ${serviceLower} project.`,
    `Whether it’s a focused update or a larger renovation, we’re ready to help.`,
  ]

  return [openers[h % openers.length], middles[(h >> 3) % middles.length], closers[(h >> 6) % closers.length]].join(
    ' ',
  )
}
