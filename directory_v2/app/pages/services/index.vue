<script setup lang="ts">
const api = usePublicApi()
const { data } = await useAsyncData('services-index', () => api.listServices())

useSeoMeta({
  title: 'Services | JobPulse',
  description: 'Browse completed projects by service category.',
})
</script>

<template>
  <div class="container">
    <section class="page-hero">
      <ProjectBreadcrumbs :items="[{ label: 'Home', to: '/' }, { label: 'Services' }]" />
      <h1>Services</h1>
      <p>Service pages exist when real project inventory supports them.</p>
    </section>
    <ServiceGrid :items="data?.items || []" />
  </div>
</template>
