<script setup lang="ts">
import { SERVICE_AREAS, areaPath } from '~/utils/siteContent'

useSeoMeta({
  title: 'Service Areas | ABC Painters',
  description: 'ABC Painters covers Acworth, Kennesaw, and Cartersville, Georgia. Three cities. That’s the list.',
})
</script>

<template>
  <div>
    <section class="page-hero">
      <div class="container">
        <AppBreadcrumbs :items="[{ label: 'Home', to: '/' }, { label: 'Service areas' }]" />
        <p class="section__eyebrow">Service areas</p>
        <h1 class="page-hero__title">Acworth, Kennesaw, Cartersville.</h1>
        <p class="section__lead">
          Three city pages. Three chips on the home page. We do not list neighborhoods we did not build pages for.
        </p>
      </div>
    </section>

    <section class="section section--tight">
      <div class="container card-grid card-grid--3">
        <NuxtLink v-for="a in SERVICE_AREAS" :key="a.slug" class="area-card" :to="areaPath(a.slug)">
          <img :src="a.image" :alt="`${a.city}, Georgia`" width="1200" height="675" />
          <div class="area-card__body">
            <h2>{{ a.city }}, {{ a.state }}</h2>
            <p>{{ a.note }}</p>
            <p>{{ a.housing }}</p>
            <span>Painting in {{ a.city }} →</span>
          </div>
        </NuxtLink>
      </div>
    </section>
  </div>
</template>

<style scoped>
.area-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  overflow: hidden;
  text-decoration: none !important;
  color: inherit;
}

.area-card:hover {
  border-color: var(--orange);
}

.area-card img {
  width: 100%;
  height: 10rem;
  object-fit: cover;
}

.area-card__body {
  padding: 1.25rem;
}

.area-card h2 {
  font-size: 1.35rem;
  color: var(--navy);
}

.area-card span {
  font-weight: 700;
  color: var(--orange);
}
</style>
