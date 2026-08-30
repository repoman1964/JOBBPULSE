<script setup lang="ts">
import type { Job } from '~/types/domain'

const api = useApi()
const currentJobs = ref<Job[]>([])
const publishedJobs = ref<Job[]>([])
const view = ref<'current' | 'published'>('current')
const loading = ref(true)
const error = ref('')
let poll: ReturnType<typeof setInterval> | null = null

const hasProcessing = computed(() =>
  currentJobs.value.some((j) => j.publicStatus === 'processing' || j.publicStatus === 'publishing'),
)

const visibleJobs = computed(() => view.value === 'current' ? currentJobs.value : publishedJobs.value)

function stopPoll() {
  if (poll) {
    clearInterval(poll)
    poll = null
  }
}

function startPoll() {
  if (poll) return
  poll = setInterval(() => {
    void load(true)
  }, 1000)
}

async function load(silent = false) {
  if (!silent) loading.value = true
  error.value = ''
  try {
    const [current, published] = await Promise.all([
      api.listJobs({ scope: 'current' }),
      api.listJobs({ scope: 'published' }),
    ])
    currentJobs.value = current.items
    publishedJobs.value = published.items
  } catch (e) {
    error.value = e instanceof Error ? e.message : 'Could not load jobs.'
  } finally {
    if (!silent) loading.value = false
    if (hasProcessing.value) startPoll()
    else stopPoll()
  }
}

onMounted(load)
onBeforeUnmount(stopPoll)
</script>

<template>
  <div>
    <JpHeader />
    <main class="app-main jobs-page">
      <div v-if="error" class="banner banner-error" role="alert">{{ error }}</div>
      <p v-if="loading" class="muted">Loading jobs…</p>

      <div v-else class="jobs-content">
        <div class="jobs-tabs" role="tablist" aria-label="Jobs views">
          <button
            type="button"
            class="jobs-tab"
            :class="{ 'jobs-tab--active': view === 'current' }"
            role="tab"
            :aria-selected="view === 'current'"
            @click="view = 'current'"
          >
            Current jobs
            <span class="jobs-tab__count">{{ currentJobs.length }}</span>
          </button>
          <button
            type="button"
            class="jobs-tab"
            :class="{ 'jobs-tab--active': view === 'published' }"
            role="tab"
            :aria-selected="view === 'published'"
            @click="view = 'published'"
          >
            Published
            <span class="jobs-tab__count">{{ publishedJobs.length }}</span>
          </button>
        </div>

        <div class="stack-lg jobs-list" role="tabpanel">
          <JobCard v-for="job in visibleJobs" :key="job.id" :job="job" />
          <p v-if="!visibleJobs.length" class="muted">
            {{ view === 'current' ? 'No current jobs. Create your first job.' : 'No published jobs yet.' }}
          </p>
        </div>
      </div>

      <div class="fab-wrap">
        <NuxtLink class="btn btn-primary btn-fab" to="/jobs/new">
          <span aria-hidden="true">＋</span>
          New Job
        </NuxtLink>
      </div>
    </main>
  </div>
</template>

<style scoped>
.jobs-page {
  padding-bottom: calc(96px + var(--jp-safe-bottom));
}

.jobs-list {
  padding-top: 8px;
}

.jobs-tabs {
  display: flex;
  gap: 8px;
  border-bottom: 1px solid var(--jp-border);
}

.jobs-tab {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  min-height: 44px;
  padding: 0 4px;
  border: 0;
  border-bottom: 3px solid transparent;
  margin-bottom: -1px;
  background: transparent;
  color: var(--jp-muted);
  font: inherit;
  font-weight: 800;
  cursor: pointer;
}

.jobs-tab--active {
  border-bottom-color: var(--jp-lime);
  color: var(--jp-text);
}

.jobs-tab__count {
  min-width: 22px;
  padding: 2px 6px;
  border-radius: 999px;
  background: var(--jp-surface-2);
  font-size: 0.75rem;
  text-align: center;
}

.fab-wrap {
  position: fixed;
  left: 50%;
  bottom: calc(20px + var(--jp-safe-bottom));
  transform: translateX(-50%);
  width: min(var(--jp-max-width), 100%);
  display: flex;
  justify-content: center;
  pointer-events: none;
  padding: 0 16px;
}

.fab-wrap .btn {
  pointer-events: auto;
  width: auto;
  min-width: 160px;
  padding-inline: 28px;
}
</style>
