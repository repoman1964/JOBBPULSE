<script setup lang="ts">
import {
  SERVICES,
  SERVICE_AREAS,
  getArea,
  areaPath,
  servicePath,
  areaServicePath,
  serviceInAreaTitle,
  reviewsForArea,
} from '~/utils/siteContent'

const route = useRoute()
const citySlug = computed(() => String(route.params.city || ''))
const area = computed(() => getArea(citySlug.value))

if (!area.value) {
  throw createError({ statusCode: 404, statusMessage: 'Service area not found' })
}

const a = area.value

useSeoMeta({
  title: `Painting in ${a.city}, ${a.state} | Red Clay`,
  description: `${a.longDescription.slice(0, 145)}… Free estimates. Kitchen cabinets, vanities & built-ins.`,
})

useHead({
  script: [
    {
      type: 'application/ld+json',
      children: JSON.stringify({
        '@context': 'https://schema.org',
        '@type': 'HomeAndConstructionBusiness',
        name: 'Red Clay',
        areaServed: {
          '@type': 'City',
          name: a.city,
          containedInPlace: { '@type': 'State', name: 'Georgia' },
        },
        description: a.longDescription,
      }),
    },
  ],
})

const crumbs = [
  { label: 'Home', to: '/' },
  { label: 'Service area', to: '/service-area' },
  { label: `${a.city}, ${a.state}` },
]

const serviceLinks = SERVICES.map((s) => ({
  to: areaServicePath(a.slug, s.slug),
  title: serviceInAreaTitle(s, a),
  subtitle: s.short,
}))

const siblingAreas = SERVICE_AREAS.filter((x) => x.slug !== a.slug).map((x) => ({
  to: areaPath(x.slug),
  title: `${x.city}, ${x.state}`,
  subtitle: x.note,
}))

const serviceHubLinks = SERVICES.map((s) => ({
  to: servicePath(s.slug),
  title: s.name,
  subtitle: 'Metro-wide service page',
}))

const localReviews = reviewsForArea(a.city)
</script>

<template>
  <div>
    <section class="page-hero">
      <div class="container">
        <AppBreadcrumbs :items="crumbs" />
        <p class="section__eyebrow">Service area</p>
        <h1 class="page-hero__title">Painting in {{ a.city }}, {{ a.state }}</h1>
        <p class="section__lead">{{ a.note }}</p>
      </div>
    </section>

    <section class="section section--tight">
      <div class="container silo-layout">
        <div>
          <article class="content-card page-body">
            <h2>Serving {{ a.city }}</h2>
            <p>{{ a.longDescription }}</p>
            <h3>Neighborhoods &amp; nearby</h3>
            <ul class="neighborhoods">
              <li v-for="n in a.neighborhoods" :key="n">{{ n }}</li>
            </ul>
          </article>

          <SiloLinkGrid
            :heading="`Services in ${a.city}`"
            :links="serviceLinks"
          />

          <div v-if="localReviews.length" class="content-card" style="margin-top: 1.5rem">
            <h2>What {{ a.city }} homeowners say</h2>
            <blockquote v-for="r in localReviews" :key="r.author" class="local-review">
              <p>“{{ r.text }}”</p>
              <footer>— {{ r.author }}, {{ r.location }}</footer>
            </blockquote>
          </div>

          <SiloLinkGrid heading="Other cities we serve" :links="siblingAreas" />
          <SiloLinkGrid heading="Service overview pages" :links="serviceHubLinks" />
        </div>

        <aside class="silo-aside">
          <div class="silo-aside__card">
            <h2>Work in {{ a.city }}?</h2>
            <p class="muted">Free estimate for kitchens, vanities, and built-ins.</p>
            <NuxtLink class="btn btn--primary" :to="`/contact?location=${a.city}`">
              Free estimate
            </NuxtLink>
            <NuxtLink class="btn btn--secondary" to="/work">Work</NuxtLink>
            <NuxtLink class="btn btn--secondary" to="/service-area">All locations</NuxtLink>
          </div>
        </aside>
      </div>
    </section>
  </div>
</template>

<style scoped>
.local-review {
  margin: 0 0 1rem;
  padding: 0;
  border: 0;
}

.local-review p {
  margin: 0 0 0.35rem;
  color: var(--ink);
  font-size: 0.98rem;
}

.local-review footer {
  font-size: 0.85rem;
  font-weight: 700;
  color: var(--muted);
}
</style>
