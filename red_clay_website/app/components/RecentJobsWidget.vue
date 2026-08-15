<script setup lang="ts">
/**
 * Above-the-fold widget: live recent jobs from JobPulse contractor app / directory API.
 * Falls back to static demo cards if the API is unreachable.
 */
import type { ProjectCard } from '~/composables/useJobPulse'
import { FALLBACK_JOBS } from '~/utils/siteContent'

const props = withDefaults(
  defineProps<{
    limit?: number
    compact?: boolean
  }>(),
  { limit: 3, compact: true },
)

const api = useJobPulse()
const jobs = ref<ProjectCard[]>([])
const source = ref<'live' | 'fallback'>('fallback')
const loading = ref(true)
const errorMsg = ref<string | null>(null)

async function load() {
  loading.value = true
  errorMsg.value = null
  try {
    const data = await api.listProjects(props.limit, 0)
    const items = data?.items || []
    if (items.length) {
      jobs.value = items
      source.value = 'live'
    } else {
      // Try contractor profile recent_projects
      const profile = await api.getContractor(props.limit)
      const recent = profile?.recent_projects || []
      if (recent.length) {
        jobs.value = recent.slice(0, props.limit)
        source.value = 'live'
      } else {
        jobs.value = FALLBACK_JOBS.slice(0, props.limit) as unknown as ProjectCard[]
        source.value = 'fallback'
      }
    }
  } catch (e: unknown) {
    jobs.value = FALLBACK_JOBS.slice(0, props.limit) as unknown as ProjectCard[]
    source.value = 'fallback'
    errorMsg.value = e instanceof Error ? e.message : 'API unavailable'
  } finally {
    loading.value = false
  }
}

onMounted(load)

// SSR: also try once on server so above-the-fold has content when API is up
if (import.meta.server) {
  await load()
}
</script>

<template>
  <section class="recent-jobs" aria-labelledby="recent-jobs-heading">
    <div class="recent-jobs__head">
      <div>
        <p class="recent-jobs__eyebrow">
          <span class="recent-jobs__pulse" :class="{ 'is-live': source === 'live' }" aria-hidden="true" />
          {{ source === 'live' ? 'Live from JobPulse' : 'Recent completed work' }}
        </p>
        <h2 id="recent-jobs-heading" class="recent-jobs__title">Just finished on the job</h2>
        <p class="recent-jobs__sub">
          Photos and write-ups from our contractor app—published to this site automatically.
        </p>
      </div>
      <NuxtLink class="recent-jobs__all" to="/portfolio">View all work →</NuxtLink>
    </div>

    <div v-if="loading && !jobs.length" class="recent-jobs__skeleton" aria-busy="true">
      <div v-for="n in limit" :key="n" class="recent-jobs__skel-card" />
    </div>

    <div v-else class="recent-jobs__grid">
      <JobCard v-for="job in jobs" :key="job.id || job.slug" :project="job" :compact="compact" />
    </div>

    <p v-if="source === 'fallback' && errorMsg" class="recent-jobs__hint">
      Showing sample jobs (API offline). Start the API and refresh for live posts.
    </p>
  </section>
</template>

<style scoped>
.recent-jobs {
  background: rgba(255, 255, 255, 0.94);
  border: 1px solid rgba(232, 221, 212, 0.95);
  border-radius: var(--radius-lg);
  padding: 1rem 1rem 1.15rem;
  box-shadow: var(--shadow-lg);
  backdrop-filter: blur(8px);
}

.recent-jobs__head {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-start;
  justify-content: space-between;
  gap: 0.75rem 1rem;
  margin-bottom: 0.9rem;
}

.recent-jobs__eyebrow {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  margin: 0 0 0.25rem;
  font-size: 0.72rem;
  font-weight: 800;
  letter-spacing: 0.07em;
  text-transform: uppercase;
  color: var(--clay);
}

.recent-jobs__pulse {
  width: 0.55rem;
  height: 0.55rem;
  border-radius: 50%;
  background: #c4b5a8;
}

.recent-jobs__pulse.is-live {
  background: #16a34a;
  box-shadow: 0 0 0 0 rgba(22, 163, 74, 0.5);
  animation: pulse 1.8s infinite;
}

@keyframes pulse {
  0% {
    box-shadow: 0 0 0 0 rgba(22, 163, 74, 0.45);
  }
  70% {
    box-shadow: 0 0 0 8px rgba(22, 163, 74, 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(22, 163, 74, 0);
  }
}

.recent-jobs__title {
  font-size: 1.15rem;
  margin: 0;
}

.recent-jobs__sub {
  margin: 0.25rem 0 0;
  font-size: 0.85rem;
  color: var(--muted);
  max-width: 28rem;
}

.recent-jobs__all {
  font-size: 0.88rem;
  font-weight: 700;
  color: var(--clay-dark);
  text-decoration: none !important;
  white-space: nowrap;
}

.recent-jobs__all:hover {
  text-decoration: underline !important;
}

.recent-jobs__grid {
  display: grid;
  gap: 0.75rem;
  grid-template-columns: 1fr;
}

@media (min-width: 640px) {
  .recent-jobs__grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

.recent-jobs__skeleton {
  display: grid;
  gap: 0.75rem;
  grid-template-columns: 1fr;
}

@media (min-width: 640px) {
  .recent-jobs__skeleton {
    grid-template-columns: repeat(3, 1fr);
  }
}

.recent-jobs__skel-card {
  height: 11rem;
  border-radius: var(--radius);
  background: linear-gradient(90deg, #f0e6dc 25%, #f7f1ea 50%, #f0e6dc 75%);
  background-size: 200% 100%;
  animation: shimmer 1.2s infinite;
}

@keyframes shimmer {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}

.recent-jobs__hint {
  margin: 0.75rem 0 0;
  font-size: 0.78rem;
  color: var(--muted);
}
</style>
