<script setup lang="ts">
const route = useRoute()
const api = usePublicApi()

const q = ref(typeof route.query.q === 'string' ? route.query.q : '')
const city = ref(typeof route.query.city === 'string' ? route.query.city : '')
const service = ref(typeof route.query.service_key === 'string' ? route.query.service_key : '')

const { data, refresh, pending } = await useAsyncData(
  'projects-index',
  () =>
    api.listProjects({
      q: q.value || undefined,
      city: city.value || undefined,
      service_key: service.value || undefined,
      limit: 30,
    }),
  { watch: [q, city, service] },
)

const { data: services } = await useAsyncData('services-filter', () => api.listServices())
const { data: locations } = await useAsyncData('locations-filter', () => api.listLocations())

useSeoMeta({
  title: 'Browse Projects | JobPulse',
  description: 'Browse completed home-service projects by local contractors.',
})

function applyFilters() {
  navigateTo({
    path: '/projects',
    query: {
      ...(q.value ? { q: q.value } : {}),
      ...(city.value ? { city: city.value } : {}),
      ...(service.value ? { service_key: service.value } : {}),
    },
  })
  refresh()
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
      <input v-model="q" type="search" placeholder="Search…" aria-label="Search" />
      <select v-model="service" aria-label="Service">
        <option value="">All services</option>
        <option v-for="s in services?.items || []" :key="s.slug" :value="s.service_key">
          {{ s.name }}
        </option>
      </select>
      <select v-model="city" aria-label="City">
        <option value="">All locations</option>
        <option v-for="loc in locations?.items || []" :key="loc.slug" :value="loc.city">
          {{ loc.name }}
        </option>
      </select>
      <button class="btn btn-primary" type="submit">Apply</button>
    </form>

    <p v-if="pending" class="muted">Loading…</p>
    <ProjectGallery
      :projects="data?.items || []"
      empty-text="No projects match these filters."
    />
  </div>
</template>
