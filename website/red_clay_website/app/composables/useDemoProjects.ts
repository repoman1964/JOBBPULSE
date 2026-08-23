import { DUMMY_JOBS, getDummyJob, type DummyJob } from '~/utils/siteContent'
import { DEMO_EMAIL_COOKIE, DEMO_EMAIL_MAX_AGE, isValidEmail, normalizeEmail } from '~/utils/demoEmail'
import { mergeLiveAndDummy, type CarouselJob } from '~/utils/demoProjects'

export type LiveProject = CarouselJob & {
  media?: { stageLabel: string; url?: string | null }[]
  socialPosts?: { destination: string; title: string; body: string; imageUrl?: string | null }[]
}

function apiBase() {
  const config = useRuntimeConfig()
  return String(config.public.apiBase || '').replace(/\/$/, '')
}

export function useDemoEmailCookie() {
  return useCookie(DEMO_EMAIL_COOKIE, {
    path: '/',
    maxAge: DEMO_EMAIL_MAX_AGE,
    sameSite: 'lax',
  })
}

export function useDemoProjects() {
  const emailCookie = useDemoEmailCookie()
  const live = useState<CarouselJob[]>('red-clay-live-jobs', () => [])

  async function fetchLiveList(): Promise<CarouselJob[]> {
    const email = emailCookie.value ? normalizeEmail(emailCookie.value) : ''
    const base = apiBase()
    if (!base || !email || !isValidEmail(email)) {
      live.value = []
      return []
    }
    try {
      const data = await $fetch<{ items: Record<string, unknown>[] }>(
        `${base}/api/v1/public/demo/projects`,
        { query: { email } },
      )
      const items = (data.items || []).map((raw) => ({
        slug: String(raw.slug || ''),
        publicTitle: String(raw.publicTitle || ''),
        publicSummary: String(raw.publicSummary || ''),
        serviceType: String(raw.serviceType || ''),
        city: String(raw.city || ''),
        publishedAt: (raw.publishedAt as string) || null,
        primaryImageUrl: (raw.primaryImageUrl as string) || null,
        hasBefore: Boolean(raw.hasBefore),
        hasAfter: Boolean(raw.hasAfter),
      }))
      live.value = items
      return items
    } catch {
      live.value = []
      return []
    }
  }

  function carouselJobs(): CarouselJob[] {
    const dummy: CarouselJob[] = DUMMY_JOBS.map((j) => ({
      slug: j.slug,
      publicTitle: j.publicTitle,
      publicSummary: j.publicSummary,
      serviceType: j.serviceType,
      city: j.city,
      publishedAt: j.publishedAt,
      primaryImageUrl: j.primaryImageUrl,
      hasBefore: j.hasBefore,
      hasAfter: j.hasAfter,
    }))
    return mergeLiveAndDummy(live.value, dummy)
  }

  async function fetchLiveDetail(slug: string): Promise<LiveProject | null> {
    const email = emailCookie.value ? normalizeEmail(emailCookie.value) : ''
    const base = apiBase()
    if (!base || !email || !isValidEmail(email)) return null
    try {
      return await $fetch<LiveProject>(
        `${base}/api/v1/public/demo/projects/${encodeURIComponent(slug)}`,
        { query: { email } },
      )
    } catch {
      return null
    }
  }

  function dummyDetail(slug: string): DummyJob | undefined {
    return getDummyJob(slug)
  }

  async function identify(email: string): Promise<{ ok: boolean; message: string; count: number }> {
    const normalized = normalizeEmail(email)
    if (!isValidEmail(normalized)) {
      return { ok: false, message: 'Enter a valid email.', count: 0 }
    }
    emailCookie.value = normalized
    if (!apiBase()) {
      return {
        ok: false,
        message: 'Could not reach the project service. Try again.',
        count: 0,
      }
    }
    try {
      const items = await fetchLiveList()
      const count = items.length
      if (!count) {
        return {
          ok: true,
          message:
            'No published project for that email yet. Finish the job in the contractor app, then try again.',
          count: 0,
        }
      }
      return { ok: true, message: `Showing ${count} project${count === 1 ? '' : 's'} for that email.`, count }
    } catch {
      return { ok: false, message: 'Could not reach the project service. Try again.', count: 0 }
    }
  }

  function clearEmail() {
    emailCookie.value = null
    live.value = []
  }

  return {
    emailCookie,
    live,
    fetchLiveList,
    carouselJobs,
    fetchLiveDetail,
    dummyDetail,
    identify,
    clearEmail,
  }
}
