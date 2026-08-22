<script setup lang="ts">
import { SERVICES, SERVICE_AREAS, getArea, servicePath, areaPath } from '~/utils/siteContent'

const route = useRoute()
const slug = computed(() => String(route.params.city || ''))
const area = computed(() => getArea(slug.value))

if (!area.value) {
  throw createError({ statusCode: 404, statusMessage: 'Service area not found' })
}

const a = area.value

useSeoMeta({
  title: `Painters in ${a.city}, GA | ABC Painters`,
  description: `Residential interior and exterior painting in ${a.city}, Georgia. ${a.note}. Free written estimates.`,
})

const siblings = SERVICE_AREAS.filter((x) => x.slug !== a.slug)
</script>

<template>
  <div>
    <section class="page-hero">
      <div class="container">
        <AppBreadcrumbs
          :items="[
            { label: 'Home', to: '/' },
            { label: 'Service areas', to: '/service-areas' },
            { label: a.city },
          ]"
        />
        <p class="section__eyebrow">{{ a.note }}</p>
        <h1 class="page-hero__title">Painters in {{ a.city }}, Georgia</h1>
        <p class="section__lead">{{ a.housing }}</p>
      </div>
    </section>

    <section class="section section--tight">
      <div class="container silo-layout">
        <div>
          <img class="detail-hero" :src="a.image" :alt="`Residential street in ${a.city}, Georgia`" />
          <article class="content-card">
            <h2>Why {{ a.city }} homeowners call ABC</h2>
            <p>{{ a.longDescription }}</p>
            <blockquote>
              <p>“{{ a.testimonial.text }}”</p>
              <footer>— {{ a.testimonial.author }} · {{ a.testimonial.job }}</footer>
            </blockquote>
            <h3>Services in {{ a.city }}</h3>
            <ul class="bullet-list">
              <li v-for="s in SERVICES" :key="s.slug">
                <NuxtLink :to="servicePath(s.slug)">{{ s.name }}</NuxtLink>
                — {{ s.short }}
              </li>
            </ul>
          </article>
        </div>
        <aside>
          <div class="silo-aside__card">
            <h2>Estimate in {{ a.city }}</h2>
            <p class="muted">Free walkthrough. Written quote before we start.</p>
            <NuxtLink class="btn btn--primary" :to="`/contact?location=${a.city}`">Free estimate</NuxtLink>
          </div>
          <div class="silo-aside__card">
            <h2>Other cities</h2>
            <p v-for="x in siblings" :key="x.slug">
              <NuxtLink :to="areaPath(x.slug)">{{ x.city }}, {{ x.state }}</NuxtLink>
            </p>
          </div>
        </aside>
      </div>
    </section>
  </div>
</template>

<style scoped>
.detail-hero {
  width: 100%;
  height: 16rem;
  object-fit: cover;
  border-radius: var(--radius-lg);
  margin-bottom: 1.25rem;
}

blockquote {
  margin: 1.25rem 0;
  padding: 1rem 1.15rem;
  border-left: 4px solid var(--orange);
  background: var(--bg);
}

blockquote p {
  color: var(--ink);
  font-weight: 500;
  margin: 0 0 0.5rem;
}

blockquote footer {
  color: var(--muted);
  font-size: 0.9rem;
}

aside {
  display: grid;
  gap: 1rem;
}
</style>
