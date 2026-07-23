<script setup lang="ts">
const route = useRoute()
const api = usePublicApi()

const q = ref(typeof route.query.q === 'string' ? route.query.q : '')
const city = ref(typeof route.query.city === 'string' ? route.query.city : '')
const service = ref(typeof route.query.service_key === 'string' ? route.query.service_key : '')

const { data, refresh, pending } = await useAsyncData(
  'search-page',
  () =>
    api.search({
      q: q.value || undefined,
      city: city.value || undefined,
      service_key: service.value || undefined,
      limit: 30,
    }),
  { watch: [() => route.fullPath] },
)

watch(
  () => route.query,
  (query) => {
    q.value = typeof query.q === 'string' ? query.q : ''
    city.value = typeof query.city === 'string' ? query.city : ''
    service.value = typeof query.service_key === 'string' ? query.service_key : ''
  },
)

useSeoMeta({
  title: 'Search | JobPulse',
  description: 'Search completed projects and local contractors.',
})

function runSearch() {
  navigateTo({
    path: '/search',
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
      <h1>Search</h1>
      <p>Projects come first. Contractors appear as a secondary result type.</p>
    </section>

    <form class="filters" @submit.prevent="runSearch">
      <input v-model="q" type="search" placeholder="e.g. exterior painting near Marietta" />
      <input v-model="city" type="text" placeholder="City" />
      <input v-model="service" type="text" placeholder="Service key" />
      <button class="btn btn-primary" type="submit">Search</button>
    </form>

    <p v-if="pending" class="muted">Searching…</p>

    <section class="section">
      <h2 class="section__title">Projects</h2>
      <ProjectGallery
        :projects="data?.projects || []"
        empty-text="No matching projects."
      />
    </section>

    <section v-if="data?.contractors?.length" class="section">
      <h2 class="section__title">Contractors</h2>
      <FeaturedContractors :contractors="data.contractors" />
    </section>
  </div>
</template>
