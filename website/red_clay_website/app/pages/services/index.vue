<script setup lang="ts">
import {
  SERVICES,
  SERVICE_AREAS,
  servicePath,
  areaPath,
  areaServicePath,
} from '~/utils/siteContent'

useSeoMeta({
  title: 'Painting services | Red Clay',
  description:
    'Exterior painting, trim and siding, decks and fences, and interior painting across metro Atlanta.',
})

const serviceLinks = SERVICES.map((s) => ({
  to: servicePath(s.slug),
  title: s.name,
  subtitle: s.short,
}))

const areaLinks = SERVICE_AREAS.map((a) => ({
  to: areaPath(a.slug),
  title: `${a.city}, ${a.state}`,
  subtitle: a.note,
}))
</script>

<template>
  <div>
    <section class="page-hero">
      <div class="container">
        <AppBreadcrumbs :items="[{ label: 'Home', to: '/' }, { label: 'Services' }]" />
        <p class="section__eyebrow">Services</p>
        <h1 class="page-hero__title">Four materials of work. One standard of prep.</h1>
        <p class="section__lead">
          Exterior-led painting — not a dozen unrelated trades. Each service has its own page, with links to every city we cover.
        </p>
      </div>
    </section>

    <section class="section section--tight">
      <div class="container services-list">
        <article v-for="s in SERVICES" :id="s.slug" :key="s.slug" class="service-block">
          <div>
            <h2>
              <NuxtLink :to="servicePath(s.slug)" class="service-block__title-link">{{ s.name }}</NuxtLink>
            </h2>
            <p>{{ s.description }}</p>
            <ul class="bullet-list">
              <li v-for="b in s.bullets" :key="b">{{ b }}</li>
            </ul>
            <div class="service-block__actions">
              <NuxtLink class="btn btn--primary" :to="servicePath(s.slug)">{{ s.name }} details</NuxtLink>
              <NuxtLink class="btn btn--secondary" :to="`/contact?service=${s.service_key}`">
                Free estimate
              </NuxtLink>
            </div>
            <p class="service-block__local muted">
              Local pages:
              <template v-for="(a, i) in SERVICE_AREAS" :key="a.slug">
                <NuxtLink :to="areaServicePath(a.slug, s.slug)">{{ a.city }}</NuxtLink>
                <span v-if="i < SERVICE_AREAS.length - 1"> · </span>
              </template>
            </p>
          </div>
        </article>

        <SiloLinkGrid heading="All services" :links="serviceLinks" />
        <SiloLinkGrid
          heading="Browse by city"
          :links="areaLinks"
        />
      </div>
    </section>
  </div>
</template>

<style scoped>
.services-list {
  display: grid;
  gap: 1.25rem;
}

.service-block {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 1.5rem;
  box-shadow: var(--shadow);
  scroll-margin-top: calc(var(--header-h) + 1rem);
}

.service-block h2 {
  margin-top: 0;
}

.service-block__title-link {
  color: inherit;
  text-decoration: none !important;
}

.service-block__title-link:hover {
  color: var(--clay-dark);
  text-decoration: underline !important;
}

.service-block__actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 0.85rem;
}

.service-block__local {
  margin: 0;
  font-size: 0.88rem;
  line-height: 1.6;
}

.service-block__local a {
  font-weight: 700;
}
</style>
