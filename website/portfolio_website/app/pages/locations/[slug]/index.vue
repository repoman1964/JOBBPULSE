<script setup lang="ts">
import { cityOnly } from '~/utils/locationLabel'

const route = useRoute()
const api = usePublicApi()
const slug = computed(() => String(route.params.slug || ''))

const { data, error } = await useAsyncData(
  () => `location-${slug.value}`,
  () => api.getLocation(slug.value),
  { watch: [slug] },
)

if (error.value) {
  throw createError({ statusCode: 404, statusMessage: 'Location not found' })
}

const location = computed(() => data.value)
const locationLabel = computed(() =>
  cityOnly(location.value?.city, location.value?.name) || 'this area',
)

useSeoMeta({
  title: () => `Projects in ${locationLabel.value} | JobPulse`,
  description: () => `Recent completed home-service projects in ${locationLabel.value}.`,
})
</script>

<template>
  <div v-if="location" class="container">
    <section class="page-hero">
      <ProjectBreadcrumbs
        :items="[
          { label: 'Home', to: '/' },
          { label: 'Locations', to: '/locations' },
          { label: locationLabel },
        ]"
      />
      <h1>Projects in {{ locationLabel }}</h1>
      <p class="muted">{{ location.project_count }} documented projects</p>
    </section>

    <section class="section">
      <ProjectGallery :projects="location.projects || []" />
    </section>

    <section v-if="location.services?.length" class="section">
      <h2 class="section__title">Services available here</h2>
      <ServiceGrid :items="location.services" />
    </section>

    <section v-if="location.contractors?.length" class="section">
      <h2 class="section__title">Contractors active in this area</h2>
      <FeaturedContractors :contractors="location.contractors" />
    </section>
  </div>
</template>
