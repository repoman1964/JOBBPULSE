<script setup lang="ts">
const api = usePublicApi()
const { data, error } = await useAsyncData('home', () => api.getHome())

useSeoMeta({
  title: 'JobPulse — Browse real local projects',
  description: 'Browse real projects completed by local contractors. Work first, then connect.',
})
</script>

<template>
  <div class="container">
    <section class="page-hero">
      <h1>Browse real projects completed by local contractors</h1>
      <p>
        JobPulse is a living local portfolio of finished home-service work — not a generic business listing directory.
      </p>
      <div class="cta-actions" style="margin-top: 1rem">
        <NuxtLink class="btn btn-primary" to="/projects">Browse projects</NuxtLink>
        <NuxtLink class="btn btn-secondary" to="/how-it-works">How it works</NuxtLink>
        <NuxtLink class="btn btn-secondary" to="/for-contractors">For contractors</NuxtLink>
      </div>
    </section>

    <p v-if="error" class="empty">Could not load projects. Is the API running on port 8000?</p>

    <template v-if="data">
      <section class="section">
        <h2 class="section__title">Recently completed projects</h2>
        <ProjectGallery
          :projects="data.recent_projects || []"
          empty-text="No published projects yet. Seed demo data or publish from the contractor app."
        />
      </section>

      <section v-if="data.featured_projects?.length" class="section">
        <h2 class="section__title">Featured projects</h2>
        <ProjectGallery :projects="data.featured_projects" />
      </section>

      <section v-if="data.featured_contractors?.length" class="section">
        <h2 class="section__title">Featured contractors</h2>
        <FeaturedContractors :contractors="data.featured_contractors" />
      </section>

      <section v-if="data.popular_services?.length" class="section">
        <h2 class="section__title">Popular services</h2>
        <ServiceGrid :items="data.popular_services" />
      </section>

      <section v-if="data.popular_locations?.length" class="section">
        <h2 class="section__title">Popular locations</h2>
        <LocationGrid :items="data.popular_locations" />
      </section>
    </template>

    <section class="cta-band">
      <h2>How JobPulse works</h2>
      <p class="muted">
        Contractors document completed jobs with photos and a short voice summary. JobPulse turns that into a public project page homeowners can browse.
      </p>
      <div class="cta-actions">
        <NuxtLink class="btn btn-primary" to="/projects">See the work</NuxtLink>
        <NuxtLink class="btn btn-secondary" to="/for-contractors">Publish your projects</NuxtLink>
      </div>
    </section>
  </div>
</template>
