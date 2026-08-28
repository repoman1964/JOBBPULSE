<script setup lang="ts">
import type { Job } from '~/types/domain'

const api = useApi()
const jobs = ref<Job[]>([])
const loading = ref(true)
const error = ref('')
let poll: ReturnType<typeof setInterval> | null = null

const hasProcessing = computed(() => jobs.value.some((j) => j.publicStatus === 'processing'))

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
    const res = await api.listJobs()
    jobs.value = res.items
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

      <div v-else class="stack-lg jobs-list">
        <JobCard v-for="job in jobs" :key="job.id" :job="job" />
        <p v-if="!jobs.length" class="muted">No jobs yet. Create your first job.</p>
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
