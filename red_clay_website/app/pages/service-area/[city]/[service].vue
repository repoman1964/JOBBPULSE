<script setup lang="ts">
import {
  SERVICES,
  SERVICE_AREAS,
  getArea,
  getService,
  areaPath,
  servicePath,
  areaServicePath,
  serviceInAreaTitle,
  serviceInAreaDescription,
  serviceInAreaIntro,
} from '~/utils/siteContent'

const route = useRoute()
const citySlug = computed(() => String(route.params.city || ''))
const serviceSlug = computed(() => String(route.params.service || ''))

const area = computed(() => getArea(citySlug.value))
const service = computed(() => getService(serviceSlug.value))

if (!area.value || !service.value) {
  throw createError({ statusCode: 404, statusMessage: 'Page not found' })
}

const a = area.value
const s = service.value
const pageTitle = serviceInAreaTitle(s, a)

useSeoMeta({
  title: `${pageTitle} | Red Clay Cabinet Installers`,
  description: serviceInAreaDescription(s, a),
})

useHead({
  script: [
    {
      type: 'application/ld+json',
      children: JSON.stringify({
        '@context': 'https://schema.org',
        '@type': 'Service',
        name: pageTitle,
        description: serviceInAreaDescription(s, a),
        provider: {
          '@type': 'HomeAndConstructionBusiness',
          name: 'Red Clay Cabinet Installers',
          areaServed: `${a.city}, ${a.state}`,
        },
        areaServed: {
          '@type': 'City',
          name: a.city,
        },
        serviceType: s.name,
      }),
    },
  ],
})

const crumbs = [
  { label: 'Home', to: '/' },
  { label: 'Service area', to: '/service-area' },
  { label: a.city, to: areaPath(a.slug) },
  { label: s.name },
]

/** Same service, other cities — horizontal silo links */
const otherCities = SERVICE_AREAS.filter((x) => x.slug !== a.slug).map((x) => ({
  to: areaServicePath(x.slug, s.slug),
  title: serviceInAreaTitle(s, x),
  subtitle: x.note,
}))

/** Same city, other services */
const otherServicesHere = SERVICES.filter((x) => x.slug !== s.slug).map((x) => ({
  to: areaServicePath(a.slug, x.slug),
  title: serviceInAreaTitle(x, a),
  subtitle: x.short,
}))

const parentLinks = [
  { to: areaPath(a.slug), title: `All services in ${a.city}`, subtitle: a.note },
  { to: servicePath(s.slug), title: `${s.name} (all cities)`, subtitle: s.short },
]
</script>

<template>
  <div>
    <section class="page-hero">
      <div class="container">
        <AppBreadcrumbs :items="crumbs" />
        <p class="section__eyebrow">{{ a.city }} · {{ s.name }}</p>
        <h1 class="page-hero__title">{{ pageTitle }}</h1>
        <p class="section__lead">
          Licensed cabinet installers serving {{ a.note.toLowerCase() }}. Free estimates from Red Clay.
        </p>
      </div>
    </section>

    <section class="section section--tight">
      <div class="container silo-layout">
        <div>
          <article class="content-card page-body">
            <h2>{{ s.name }} for {{ a.city }} homes</h2>
            <p>{{ serviceInAreaIntro(s, a) }}</p>
            <p>{{ a.longDescription }}</p>
            <h3>What we deliver</h3>
            <ul class="bullet-list">
              <li v-for="b in s.bullets" :key="b">{{ b }}</li>
            </ul>
            <h3>Neighborhoods near {{ a.city }}</h3>
            <ul class="neighborhoods">
              <li v-for="n in a.neighborhoods" :key="n">{{ n }}</li>
            </ul>
            <p style="margin-top: 1rem">
              See the metro-wide
              <NuxtLink :to="servicePath(s.slug)">{{ s.name }}</NuxtLink>
              overview or the
              <NuxtLink :to="areaPath(a.slug)">{{ a.city }} service area</NuxtLink>
              hub for more options.
            </p>
          </article>

          <SiloLinkGrid heading="Parent pages" :links="parentLinks" />

          <SiloLinkGrid
            :heading="`${s.name} in other cities`"
            :links="otherCities"
          />

          <SiloLinkGrid
            :heading="`More services in ${a.city}`"
            :links="otherServicesHere"
          />
        </div>

        <aside class="silo-aside">
          <div class="silo-aside__card">
            <h2>Estimate in {{ a.city }}</h2>
            <p class="muted">{{ s.name }} — free, no pressure.</p>
            <NuxtLink
              class="btn btn--primary"
              :to="`/contact?service=${s.service_key}&location=${encodeURIComponent(a.city)}`"
            >
              Request free estimate
            </NuxtLink>
            <NuxtLink class="btn btn--secondary" :to="areaPath(a.slug)">
              {{ a.city }} overview
            </NuxtLink>
            <NuxtLink class="btn btn--secondary" :to="servicePath(s.slug)">
              {{ s.name }} overview
            </NuxtLink>
          </div>
        </aside>
      </div>
    </section>
  </div>
</template>
