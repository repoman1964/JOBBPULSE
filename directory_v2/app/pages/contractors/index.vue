<script setup lang="ts">
const api = usePublicApi()
const { data } = await useAsyncData('contractors-index', () => api.listContractors({ limit: 40 }))

useSeoMeta({
  title: 'Contractors | JobPulse',
  description: 'Contractors with documented completed projects on JobPulse.',
})
</script>

<template>
  <div class="container">
    <section class="page-hero">
      <ProjectBreadcrumbs :items="[{ label: 'Home', to: '/' }, { label: 'Contractors' }]" />
      <h1>Contractors</h1>
      <p>Browse contractors by their body of completed work — not marketing copy alone.</p>
    </section>
    <FeaturedContractors :contractors="data?.items || []" />
    <div v-if="!(data?.items?.length)" class="empty">No published contractors yet.</div>
  </div>
</template>
