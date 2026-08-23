import { describe, expect, it } from 'vitest'
import { DUMMY_JOBS, NAV_LABELS, PUBLIC_CHROME_COPY } from '../app/utils/siteContent'
import { isDummySlug, mergeLiveAndDummy, publicChromeHasForbiddenWords } from '../app/utils/demoProjects'
import { isValidEmail } from '../app/utils/demoEmail'

describe('dummy jobs', () => {
  it('reserves demo- slug prefixes', () => {
    expect(DUMMY_JOBS.length).toBeGreaterThanOrEqual(4)
    for (const job of DUMMY_JOBS) {
      expect(isDummySlug(job.slug)).toBe(true)
    }
  })
})

describe('mergeLiveAndDummy', () => {
  it('prepends live jobs and dedupes by slug', () => {
    const live = [
      {
        slug: 'exterior-painting-in-decatur-a1b2',
        publicTitle: 'Exterior painting in Decatur',
        publicSummary: 'Live job',
        serviceType: 'Exterior painting',
        city: 'Decatur',
        hasBefore: true,
        hasAfter: true,
      },
      {
        slug: DUMMY_JOBS[0].slug,
        publicTitle: 'Duplicate dummy slug from API',
        publicSummary: 'Should lose to first occurrence',
        serviceType: 'Exterior painting',
        city: 'Atlanta',
        hasBefore: true,
        hasAfter: true,
      },
    ]
    const merged = mergeLiveAndDummy(live, [...DUMMY_JOBS])
    expect(merged[0].slug).toBe('exterior-painting-in-decatur-a1b2')
    expect(merged.filter((j) => j.slug === DUMMY_JOBS[0].slug)).toHaveLength(1)
    expect(merged.length).toBe(1 + DUMMY_JOBS.length)
  })
})

describe('public chrome', () => {
  it('does not include JobbPulse', () => {
    for (const text of [...NAV_LABELS, ...PUBLIC_CHROME_COPY]) {
      expect(publicChromeHasForbiddenWords(text)).toBe(false)
    }
  })
})

describe('email', () => {
  it('accepts a normal address', () => {
    expect(isValidEmail('Alex@Example.com')).toBe(true)
    expect(isValidEmail('nope')).toBe(false)
  })
})
