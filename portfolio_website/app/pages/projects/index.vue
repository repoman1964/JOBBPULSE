<script setup lang="ts">
import { cityOnly } from '~/utils/locationLabel'

const route = useRoute()
const api = usePublicApi()
const nuxtApp = useNuxtApp()

const q = computed(() => (typeof route.query.q === 'string' ? route.query.q : ''))
const city = computed(() => (typeof route.query.city === 'string' ? route.query.city : ''))
const service = computed(() =>
  typeof route.query.service_key === 'string' ? route.query.service_key : '',
)

const qInput = ref(q.value)
const cityInput = ref(city.value)
const serviceInput = ref(service.value)

watch(
  () => [q.value, city.value, service.value] as const,
  ([nextQ, nextCity, nextService]) => {
    qInput.value = nextQ
    cityInput.value = nextCity
    serviceInput.value = nextService
  },
)

const { data, refresh, pending, error } = await useAsyncData(
  () => `projects-index-${q.value}-${city.value}-${service.value}`,
  () =>
    api.listProjects({
      q: q.value || undefined,
      city: city.value || undefined,
      service_key: service.value || undefined,
      limit: 30,
    }),
  {
    watch: [q, city, service],
    getCachedData(key) {
      if (nuxtApp.isHydrating) return nuxtApp.payload.data[key]
      return undefined
    },
  },
)

const { data: services } = await useAsyncData('services-filter', () => api.listServices())
const { data: locations } = await useAsyncData('locations-filter', () => api.listLocations())

useSeoMeta({
  title: 'Browse Projects | JobPulse',
  description: 'Browse completed home-service projects by local contractors.',
})

function applyFilters() {
  return navigateTo({
    path: '/projects',
    query: {
      ...(qInput.value ? { q: qInput.value } : {}),
      ...(cityInput.value ? { city: cityInput.value } : {}),
      ...(serviceInput.value ? { service_key: serviceInput.value } : {}),
    },
  })
}
</script>

<template>
  <div class="container">
    <section class="page-hero">
      <ProjectBreadcrumbs :items="[{ label: 'Home', to: '/' }, { label: 'Projects' }]" />
      <h1>Browse projects</h1>
      <p>Real completed work from local contractors. Filter by service or city.</p>
    </section>

    <form class="filters" @submit.prevent="applyFilters">
      <input v-model="qInput" type="search" placeholder="Search…" aria-label="Search" />
      <select v-model="serviceInput" aria-label="Service">
        <option value="">All services</option>
        <option v-for="s in services?.items || []" :key="s.slug" :value="s.service_key">
          {{ s.name }}
        </option>
      </select>
      <select v-model="cityInput" aria-label="City">
        <option value="">All locations</option>
        <option v-for="loc in locations?.items || []" :key="loc.slug" :value="loc.city">
          {{ cityOnly(loc.city, loc.name) }}
        </option>
      </select>
      <button class="btn btn-primary" type="submit">Apply</button>
    </form>

    <p v-if="pending" class="muted">Loading…</p>
    <p v-else-if="error" class="empty">
      Could not load projects.
      <button type="button" class="btn btn-secondary" style="margin-left: 0.5rem" @click="refresh()">
        Retry
      </button>
    </p>
    <ProjectGallery
      v-else
      :projects="data?.items || []"
      empty-text="No projects match these filters."
    />
  </div>
</template>
