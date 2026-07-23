<script setup lang="ts">
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

useSeoMeta({
  title: () => `Projects in ${location.value?.name || 'this area'} | JobPulse`,
  description: () => `Recent completed home-service projects in ${location.value?.name || 'this area'}.`,
})
</script>

<template>
  <div v-if="location" class="container">
    <section class="page-hero">
      <ProjectBreadcrumbs
        :items="[
          { label: 'Home', to: '/' },
          { label: 'Locations', to: '/locations' },
          { label: location.name },
        ]"
      />
      <h1>Projects in {{ location.name }}</h1>
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
