import { DUMMY_JOBS, getDummyJob, type DummyJob } from '~/utils/siteContent'
import { DEMO_EMAIL_COOKIE, DEMO_EMAIL_MAX_AGE, isValidEmail, normalizeEmail } from '~/utils/demoEmail'
import { mergeLiveAndDummy, parseDemoListPayload, type CarouselJob } from '~/utils/demoProjects'

export type LiveProject = CarouselJob & {
  media?: { stageLabel: string; url?: string | null }[]
  socialPosts?: {
    destination: string
    title: string
    body: string
    imageUrl?: string | null
    groupName?: string | null
  }[]
}

function apiBase() {
  const config = useRuntimeConfig()
  return String(config.public.apiBase || '').replace(/\/$/, '')
}

export function useDemoEmailCookie() {
  return useCookie<string | null>(DEMO_EMAIL_COOKIE, {
    path: '/',
    maxAge: DEMO_EMAIL_MAX_AGE,
    sameSite: 'lax',
    httpOnly: false,
    default: () => null,
  })
}

function dummyCarouselJobs(): CarouselJob[] {
  return DUMMY_JOBS.map((j) => ({
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
}

export function useDemoProjects() {
  const emailCookie = useDemoEmailCookie()
  const live = useState<CarouselJob[]>('red-clay-live-jobs', () => [])
  const fetchError = useState<string | null>('red-clay-live-jobs-error', () => null)

  async function fetchLiveList(): Promise<CarouselJob[]> {
    const email = emailCookie.value ? normalizeEmail(String(emailCookie.value)) : ''
    const base = apiBase()
    if (!base || !email || !isValidEmail(email)) {
      live.value = []
      fetchError.value = null
      return []
    }
    try {
      const payload = await $fetch(`${base}/api/v1/public/demo/projects`, {
        query: { email },
        credentials: 'omit',
        cache: 'no-store',
      })
      const items = parseDemoListPayload(payload)
      live.value = items
      fetchError.value = null
      return items
    } catch {
      fetchError.value = 'Could not reach the project service. Try again.'
      return live.value
    }
  }

  function carouselJobs(): CarouselJob[] {
    return mergeLiveAndDummy(live.value, dummyCarouselJobs())
  }

  const jobs = computed(() => carouselJobs())

  async function fetchLiveDetail(slug: string): Promise<LiveProject | null> {
    const email = emailCookie.value ? normalizeEmail(String(emailCookie.value)) : ''
    const base = apiBase()
    if (!base || !email || !isValidEmail(email)) return null
    try {
      const payload = await $fetch<LiveProject & { data?: LiveProject }>(
        `${base}/api/v1/public/demo/projects/${encodeURIComponent(slug)}`,
        { query: { email }, credentials: 'omit', cache: 'no-store' },
      )
      return payload.data || payload
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
    const previous = live.value
    live.value = []
    const items = await fetchLiveList()
    if (fetchError.value) {
      live.value = previous
      return { ok: false, message: fetchError.value, count: 0 }
    }
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
  }

  function clearEmail() {
    emailCookie.value = null
    live.value = []
    fetchError.value = null
  }

  onMounted(() => {
    void fetchLiveList()
  })

  return {
    emailCookie,
    live,
    jobs,
    fetchLiveList,
    carouselJobs,
    fetchLiveDetail,
    dummyDetail,
    identify,
    clearEmail,
  }
}
