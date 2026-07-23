<script setup lang="ts">
const api = usePublicApi()
const { data } = await useAsyncData('locations-index', () => api.listLocations())

useSeoMeta({
  title: 'Locations | JobPulse',
  description: 'Browse completed projects by city and service area.',
})
</script>

<template>
  <div class="container">
    <section class="page-hero">
      <ProjectBreadcrumbs :items="[{ label: 'Home', to: '/' }, { label: 'Locations' }]" />
      <h1>Locations</h1>
      <p>City pages are generated from real completed projects — not empty keyword shells.</p>
    </section>
    <LocationGrid :items="data?.items || []" />
  </div>
</template>
