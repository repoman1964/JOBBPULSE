<script setup lang="ts">
import {
  SERVICES,
  SERVICE_AREAS,
  getService,
  servicePath,
  areaPath,
  areaServicePath,
  serviceInAreaTitle,
} from '~/utils/siteContent'

const route = useRoute()
const slug = computed(() => String(route.params.slug || ''))
const service = computed(() => getService(slug.value))

if (!service.value) {
  throw createError({ statusCode: 404, statusMessage: 'Service not found' })
}

const s = service.value

useSeoMeta({
  title: `${s.name} | Red Clay`,
  description: `${s.description.slice(0, 150)} Serving metro Atlanta. Written estimates.`,
})

useHead({
  script: [
    {
      type: 'application/ld+json',
      children: JSON.stringify({
        '@context': 'https://schema.org',
        '@type': 'Service',
        name: s.name,
        description: s.longDescription,
        provider: {
          '@type': 'HomeAndConstructionBusiness',
          name: 'Red Clay',
          areaServed: SERVICE_AREAS.map((a) => `${a.city}, ${a.state}`),
        },
        areaServed: SERVICE_AREAS.map((a) => ({
          '@type': 'City',
          name: a.city,
        })),
      }),
    },
  ],
})

const crumbs = [
  { label: 'Home', to: '/' },
  { label: 'Services', to: '/services' },
  { label: s.name },
]

const locationLinks = SERVICE_AREAS.map((a) => ({
  to: areaServicePath(a.slug, s.slug),
  title: serviceInAreaTitle(s, a),
  subtitle: a.note,
}))

const siblingServices = SERVICES.filter((x) => x.slug !== s.slug).map((x) => ({
  to: servicePath(x.slug),
  title: x.name,
  subtitle: x.short,
}))

const areaHubLinks = SERVICE_AREAS.map((a) => ({
  to: areaPath(a.slug),
  title: `${a.city}, ${a.state}`,
  subtitle: a.note,
}))
</script>

<template>
  <div>
    <section class="page-hero">
      <div class="container">
        <AppBreadcrumbs :items="crumbs" />
        <p class="section__eyebrow">Service</p>
        <h1 class="page-hero__title">{{ s.name }}</h1>
        <p class="section__lead">{{ s.short }}</p>
      </div>
    </section>

    <section class="section section--tight">
      <div class="container silo-layout">
        <div>
          <article class="content-card page-body">
            <h2>About this service</h2>
            <p>{{ s.longDescription }}</p>
            <h3>What’s included</h3>
            <ul class="bullet-list">
              <li v-for="b in s.bullets" :key="b">{{ b }}</li>
            </ul>
            <p>
              Prefer a city-specific page? Jump to
              <NuxtLink :to="areaServicePath('atlanta', s.slug)">{{ s.name }} in Atlanta</NuxtLink>
              or pick any metro city below.
            </p>
            <h3>Questions</h3>
            <details v-for="(item, i) in s.faqs" :key="item.q" class="faq" :open="i === 0">
              <summary>{{ item.q }}</summary>
              <p>{{ item.a }}</p>
            </details>
          </article>

          <SiloLinkGrid
            :heading="`${s.name} by city`"
            :links="locationLinks"
          />

          <SiloLinkGrid heading="Other services" :links="siblingServices" />

          <SiloLinkGrid heading="Service area hubs" :links="areaHubLinks" />
        </div>

        <aside class="silo-aside">
          <div class="silo-aside__card">
            <h2>Get an estimate</h2>
            <p class="muted">Tell us about your {{ s.name.toLowerCase() }} project.</p>
            <NuxtLink class="btn btn--primary" to="/book">Book an estimate</NuxtLink>
            <NuxtLink class="btn btn--secondary" to="/work">See work</NuxtLink>
            <NuxtLink class="btn btn--secondary" to="/services">All services</NuxtLink>
          </div>
        </aside>
      </div>
    </section>
  </div>
</template>
