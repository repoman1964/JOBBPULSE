<script setup lang="ts">
import type { ProjectCard } from '~/composables/useJobPulse'
import { FALLBACK_JOBS } from '~/utils/siteContent'

useSeoMeta({
  title: 'Portfolio | Red Clay Cabinet Installers',
  description: 'Recent kitchen, vanity, and built-in projects completed across metro Atlanta.',
})

const api = useJobPulse()
const projects = ref<ProjectCard[]>([])
const live = ref(false)
const loading = ref(true)

async function load() {
  loading.value = true
  try {
    const data = await api.listProjects(24, 0)
    if (data?.items?.length) {
      projects.value = data.items
      live.value = true
    } else {
      const profile = await api.getContractor(24)
      projects.value = profile?.recent_projects?.length
        ? profile.recent_projects
        : (FALLBACK_JOBS as unknown as ProjectCard[])
      live.value = Boolean(profile?.recent_projects?.length)
    }
  } catch {
    projects.value = FALLBACK_JOBS as unknown as ProjectCard[]
    live.value = false
  } finally {
    loading.value = false
  }
}

await load()
</script>

<template>
  <div>
    <section class="page-hero">
      <div class="container">
        <p class="section__eyebrow">Portfolio</p>
        <h1 class="page-hero__title">Completed work across metro Atlanta</h1>
        <p class="section__lead">
          <span v-if="live" class="badge badge--live">Live from JobPulse</span>
          <span v-else class="badge">Demo inventory</span>
          &nbsp;Each project can publish from our contractor app after the crew finishes and we approve the post.
        </p>
      </div>
    </section>

    <section class="section section--tight">
      <div class="container">
        <div v-if="loading" class="muted">Loading projects…</div>
        <div v-else class="card-grid card-grid--2 card-grid--3">
          <JobCard v-for="p in projects" :key="p.id || p.slug" :project="p" />
        </div>
        <p v-if="!projects.length" class="muted">No published projects yet. Check back after the next install.</p>
      </div>
    </section>
  </div>
</template>

<style scoped>
.page-hero {
  padding: 2.5rem 0 1rem;
  background: var(--clay-mist);
  border-bottom: 1px solid var(--border);
}

.page-hero__title {
  font-size: clamp(1.75rem, 3vw, 2.25rem);
}
</style>
