<script setup lang="ts">
const route = useRoute()
const api = usePublicApi()
const locationSlug = computed(() => String(route.params.slug || ''))
const serviceSlug = computed(() => String(route.params.service || ''))

const { data, error } = await useAsyncData(
  () => `location-service-${locationSlug.value}-${serviceSlug.value}`,
  () => api.getLocationService(locationSlug.value, serviceSlug.value),
  { watch: [locationSlug, serviceSlug] },
)

if (error.value) {
  throw createError({
    statusCode: 404,
    statusMessage: 'No published projects for this service in this location',
  })
}

const page = computed(() => data.value)

useSeoMeta({
  title: () => page.value?.title || 'Local projects | JobPulse',
  description: () =>
    `${page.value?.project_count || 0} documented ${page.value?.service?.name || ''} projects in ${page.value?.location?.name || 'this area'}.`,
})
</script>

<template>
  <div v-if="page" class="container">
    <section class="page-hero">
      <ProjectBreadcrumbs
        :items="[
          { label: 'Home', to: '/' },
          { label: 'Locations', to: '/locations' },
          { label: page.location.name, to: page.location.public_path },
          { label: page.service.name },
        ]"
      />
      <h1>{{ page.title }}</h1>
      <p class="muted">{{ page.project_count }} documented projects</p>
    </section>

    <section class="section">
      <ProjectGallery :projects="page.projects || []" />
    </section>

    <section v-if="page.contractors?.length" class="section">
      <h2 class="section__title">Contractors with relevant experience</h2>
      <FeaturedContractors :contractors="page.contractors" />
    </section>

    <section class="cta-band">
      <h2>Need similar work in {{ page.location.name }}?</h2>
      <p class="muted">Browse a project and request an estimate from the contractor who completed it.</p>
    </section>
  </div>
</template>
