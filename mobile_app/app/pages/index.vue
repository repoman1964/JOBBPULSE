<template>
  <div>
    <header style="padding: 16px 16px 8px; display: flex; justify-content: space-between; align-items: center;">
      <div>
        <div class="wordmark" style="font-size: 22px;">Job<span>Pulse</span></div>
        <div class="muted">Contractor app scaffold</div>
      </div>
      <span class="muted" style="font-size: 12px;">Phase 0</span>
    </header>

    <div class="page-body">
      <div class="card" style="margin-bottom: 12px;">
        <h1 style="margin: 0 0 8px; font-size: 20px;">Ready to capture jobs</h1>
        <p class="muted" style="margin: 0 0 16px;">
          Create a job, save before photos, come back for after photos and a voice summary.
          AI content and publishing come next.
        </p>
        <button class="btn btn-primary btn-block" type="button" @click="goCreate">
          Create Job
        </button>
      </div>

      <div class="card">
        <div style="font-weight: 600; margin-bottom: 8px;">API status</div>
        <p class="muted" style="margin: 0;">
          {{ apiStatus }}
        </p>
      </div>
    </div>

    <button class="fab" type="button" aria-label="Create job" @click="goCreate">+</button>

    <nav class="bottom-nav">
      <a href="/" class="active">Jobs</a>
      <a href="/create">Capture</a>
      <a href="/account">Account</a>
    </nav>
  </div>
</template>

<script setup lang="ts">
const config = useRuntimeConfig()
const apiStatus = ref('Checking…')

function goCreate() {
  navigateTo('/create')
}

onMounted(async () => {
  try {
    const res = await fetch(`${config.public.apiBase}/health`)
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    const data = await res.json()
    apiStatus.value = `API healthy (${data.status}) at ${config.public.apiBase}`
  } catch (err) {
    apiStatus.value = `API unreachable at ${config.public.apiBase}. Run: make api-dev`
  }
})
</script>
