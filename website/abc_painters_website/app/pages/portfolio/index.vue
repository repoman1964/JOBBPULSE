<script setup lang="ts">
import { PROJECTS, SERVICES, servicePath, areaPath } from '~/utils/siteContent'

useSeoMeta({
  title: 'Portfolio | ABC Painters',
  description: 'Interior, exterior, and cabinet painting projects in Acworth, Kennesaw, and Cartersville, Georgia.',
})

function serviceName(slug: string) {
  return SERVICES.find((s) => s.slug === slug)?.name || slug
}

function citySlug(city: string) {
  return city.toLowerCase()
}
</script>

<template>
  <div>
    <section class="page-hero">
      <div class="container">
        <AppBreadcrumbs :items="[{ label: 'Home', to: '/' }, { label: 'Portfolio' }]" />
        <p class="section__eyebrow">Portfolio</p>
        <h1 class="page-hero__title">Finished work in the three cities we cover</h1>
        <p class="section__lead">
          One project per city on this page — the same count as our service area. No phantom galleries.
        </p>
      </div>
    </section>

    <section class="section section--tight">
      <div class="container card-grid card-grid--3">
        <article v-for="p in PROJECTS" :key="p.slug" class="project">
          <img :src="p.image" :alt="p.title" width="800" height="600" />
          <div class="project__body">
            <h2>{{ p.title }}</h2>
            <p>{{ p.summary }}</p>
            <p class="project__links">
              <NuxtLink :to="servicePath(p.serviceSlug)">{{ serviceName(p.serviceSlug) }}</NuxtLink>
              ·
              <NuxtLink :to="areaPath(citySlug(p.city))">{{ p.city }}</NuxtLink>
            </p>
          </div>
        </article>
      </div>
    </section>
  </div>
</template>

<style scoped>
.project {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  overflow: hidden;
}

.project img {
  width: 100%;
  height: 14rem;
  object-fit: cover;
}

.project__body {
  padding: 1.25rem;
}

.project h2 {
  font-size: 1.25rem;
  color: var(--navy);
}

.project__links {
  font-weight: 600;
  margin: 0;
}

.project__links a {
  color: var(--orange);
}
</style>
