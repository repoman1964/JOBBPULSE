<script setup lang="ts">
import {
  SERVICE_AREAS,
  SERVICES,
  areaPath,
  servicePath,
  areaServicePath,
} from '~/utils/siteContent'

useSeoMeta({
  title: 'Service Area | Red Clay Cabinet Installers',
  description:
    'Cabinet installation in Atlanta, Decatur, Marietta, Roswell, Sandy Springs, and Brookhaven. Browse city pages and local services.',
})

const areaLinks = SERVICE_AREAS.map((a) => ({
  to: areaPath(a.slug),
  title: `${a.city}, ${a.state}`,
  subtitle: a.note,
}))

const serviceLinks = SERVICES.map((s) => ({
  to: servicePath(s.slug),
  title: s.name,
  subtitle: s.short,
}))
</script>

<template>
  <div>
    <section class="page-hero">
      <div class="container">
        <AppBreadcrumbs :items="[{ label: 'Home', to: '/' }, { label: 'Service area' }]" />
        <p class="section__eyebrow">Service area</p>
        <h1 class="page-hero__title">Metro Atlanta, neighborhood by neighborhood</h1>
        <p class="section__lead">
          Each city has its own page with services we install there. If you’re just outside these cities, still
          reach out—we often schedule nearby jobs.
        </p>
      </div>
    </section>

    <section class="section section--tight">
      <div class="container">
        <div class="card-grid card-grid--2 card-grid--3">
          <article v-for="a in SERVICE_AREAS" :key="a.slug" class="area-card">
            <h2>
              <NuxtLink :to="areaPath(a.slug)" class="area-card__link">{{ a.city }}, {{ a.state }}</NuxtLink>
            </h2>
            <p>{{ a.note }}</p>
            <p class="area-card__services muted">
              <template v-for="(s, i) in SERVICES" :key="s.slug">
                <NuxtLink :to="areaServicePath(a.slug, s.slug)">{{ s.name }}</NuxtLink>
                <span v-if="i < SERVICES.length - 1"> · </span>
              </template>
            </p>
            <NuxtLink class="area-card__more" :to="areaPath(a.slug)">{{ a.city }} location page →</NuxtLink>
          </article>
        </div>

        <SiloLinkGrid heading="All locations" :links="areaLinks" />
        <SiloLinkGrid heading="Services we install" :links="serviceLinks" />

        <div class="cta-box">
          <div>
            <h2>Not sure if we cover you?</h2>
            <p class="muted">Send your city or ZIP with the estimate form—we’ll confirm quickly.</p>
          </div>
          <NuxtLink class="btn btn--primary" to="/contact">Ask about your area</NuxtLink>
        </div>
      </div>
    </section>
  </div>
</template>

<style scoped>
.area-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 1.15rem;
  box-shadow: var(--shadow);
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.area-card h2 {
  margin: 0;
  font-size: 1.15rem;
}

.area-card__link {
  color: inherit;
  text-decoration: none !important;
}

.area-card__link:hover {
  color: var(--clay-dark);
  text-decoration: underline !important;
}

.area-card p {
  margin: 0;
}

.area-card__services {
  font-size: 0.82rem;
  line-height: 1.55;
}

.area-card__services a {
  font-weight: 700;
}

.area-card__more {
  margin-top: 0.5rem;
  font-size: 0.88rem;
  font-weight: 700;
  color: var(--clay-dark);
  text-decoration: none !important;
}

.area-card__more:hover {
  text-decoration: underline !important;
}
</style>
