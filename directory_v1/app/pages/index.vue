<template>
  <div class="shell">
    <header class="header">
      <div class="wordmark">Job<span>Pulse</span> Directory</div>
      <span class="muted" style="font-size: 13px;">Local project proof</span>
    </header>

    <section class="hero">
      <h1>Local proof of completed work</h1>
      <p class="muted">
        Before-and-after projects from home-service contractors — city-level location only,
        no street addresses.
      </p>
    </section>

    <section v-if="pending" class="hero" style="margin-top: 16px;">
      <p class="muted">Loading projects…</p>
    </section>

    <section v-else-if="errorMsg" class="hero" style="margin-top: 16px;">
      <p class="muted">{{ errorMsg }}</p>
      <p class="muted" style="font-size: 13px;">
        Is the API running at {{ apiBase }}?
      </p>
    </section>

    <section v-else style="margin-top: 16px;">
      <h2 style="font-size: 1.1rem; margin: 0 0 12px;">Recent projects</h2>
      <div v-if="!projects.length" class="hero">
        <p class="muted">No published projects yet. Approve a job in the contractor app and tap Publish.</p>
      </div>
      <div v-else class="grid project-grid">
        <NuxtLink
          v-for="p in projects"
          :key="p.slug"
          :to="p.public_path"
          class="tile project-card"
        >
          <strong>{{ p.public_title }}</strong>
          <span class="muted" style="font-size: 13px;">
            {{ [p.city, p.state].filter(Boolean).join(', ') || 'Local' }}
            <template v-if="p.service_key"> · {{ formatService(p.service_key) }}</template>
          </span>
          <span v-if="p.contractor?.company_name" class="muted" style="font-size: 12px;">
            {{ p.contractor.company_name }}
          </span>
        </NuxtLink>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
const config = useRuntimeConfig()
const apiBase = config.public.apiBase
const api = usePublicApi()

const { data, pending, error } = await useAsyncData('home-projects', () =>
  api.listProjects({ limit: 24 }),
)

const projects = computed(() => data.value?.items || [])
const errorMsg = computed(() => (error.value ? 'Could not load public projects.' : ''))

function formatService(key: string) {
  return key.replace(/_/g, ' ')
}

useSeoMeta({
  title: 'JobPulse Local Directory',
  description:
    'Local project proof for home-service contractors — before and after work that actually happened.',
})
</script>

<style scoped>
.project-grid {
  grid-template-columns: 1fr;
}
@media (min-width: 640px) {
  .project-grid {
    grid-template-columns: 1fr 1fr;
  }
}
.project-card {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 16px;
  background: var(--jp-surface);
  color: inherit;
  transition: border-color 0.15s;
}
.project-card:hover {
  border-color: var(--jp-primary);
}
</style>
