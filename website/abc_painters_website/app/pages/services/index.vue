<script setup lang="ts">
import { SERVICES, SERVICE_AREAS, servicePath, areaPath } from '~/utils/siteContent'

useSeoMeta({
  title: 'Painting Services | ABC Painters',
  description:
    'Interior painting, exterior painting, and cabinet refinishing in Acworth, Kennesaw, and Cartersville, GA.',
})
</script>

<template>
  <div>
    <section class="page-hero">
      <div class="container">
        <AppBreadcrumbs :items="[{ label: 'Home', to: '/' }, { label: 'Services' }]" />
        <p class="section__eyebrow">Our services</p>
        <h1 class="page-hero__title">Every paint job, done properly.</h1>
        <p class="section__lead">
          Three services. One local crew. Written quotes, prep-first work, two-year workmanship warranty.
        </p>
      </div>
    </section>

    <section class="section section--tight">
      <div class="container">
        <article v-for="s in SERVICES" :id="s.slug" :key="s.slug" class="service-block">
          <img :src="s.image" :alt="s.name" width="800" height="600" />
          <div>
            <h2>
              <NuxtLink :to="servicePath(s.slug)">{{ s.name }}</NuxtLink>
            </h2>
            <p>{{ s.description }}</p>
            <ul class="bullet-list">
              <li v-for="b in s.bullets" :key="b">{{ b }}</li>
            </ul>
            <div class="service-block__actions">
              <NuxtLink class="btn btn--primary" :to="servicePath(s.slug)">{{ s.name }} details</NuxtLink>
              <NuxtLink class="btn btn--secondary" :to="`/contact?service=${s.service_key}`">Free estimate</NuxtLink>
            </div>
            <p class="muted local-links">
              Also serving
              <template v-for="(a, i) in SERVICE_AREAS" :key="a.slug">
                <NuxtLink :to="areaPath(a.slug)">{{ a.city }}</NuxtLink>
                <span v-if="i < SERVICE_AREAS.length - 1"> · </span>
              </template>
            </p>
          </div>
        </article>
      </div>
    </section>
  </div>
</template>

<style scoped>
.service-block {
  display: grid;
  gap: 1.5rem;
  padding: 2rem 0;
  border-bottom: 1px solid var(--border);
}

.service-block:first-child {
  padding-top: 0;
}

@media (min-width: 800px) {
  .service-block {
    grid-template-columns: 18rem 1fr;
    align-items: start;
  }
}

.service-block img {
  width: 100%;
  height: 14rem;
  object-fit: cover;
  border-radius: var(--radius-lg);
}

.service-block h2 a {
  color: var(--navy);
  text-decoration: none;
}

.service-block h2 a:hover {
  color: var(--orange);
}

.service-block__actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.6rem;
  margin-bottom: 0.75rem;
}

.local-links a {
  font-weight: 600;
}
</style>
