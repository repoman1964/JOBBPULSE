<script setup lang="ts">
const route = useRoute()
const api = usePublicApi()
const slug = computed(() => String(route.params.slug || ''))

const { data, error } = await useAsyncData(
  () => `service-${slug.value}`,
  () => api.getService(slug.value),
  { watch: [slug] },
)

if (error.value) {
  throw createError({ statusCode: 404, statusMessage: 'Service not found' })
}

const service = computed(() => data.value)

useSeoMeta({
  title: () => `${service.value?.name || 'Service'} projects | JobPulse`,
  description: () => service.value?.description || '',
})
</script>

<template>
  <div v-if="service" class="container">
    <section class="page-hero">
      <ProjectBreadcrumbs
        :items="[
          { label: 'Home', to: '/' },
          { label: 'Services', to: '/services' },
          { label: service.name },
        ]"
      />
      <h1>Recent {{ service.name }} projects</h1>
      <p>{{ service.description }}</p>
      <p class="muted">{{ service.project_count }} documented projects</p>
    </section>

    <section class="section">
      <ProjectGallery :projects="service.projects || []" />
    </section>

    <section v-if="service.locations?.length" class="section">
      <h2 class="section__title">Where this work is documented</h2>
      <LocationGrid
        :items="
          service.locations.map((l) => ({
            slug: l.slug,
            name: `${l.city}${l.state ? ', ' + l.state : ''}`,
            project_count: l.project_count,
            public_path: l.public_path,
          }))
        "
      />
    </section>

    <section v-if="service.contractors?.length" class="section">
      <h2 class="section__title">Contractors with relevant work</h2>
      <FeaturedContractors :contractors="service.contractors" />
    </section>
  </div>
</template>
