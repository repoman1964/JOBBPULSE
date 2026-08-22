<script setup lang="ts">
import { SERVICES, SERVICE_AREAS, getService, servicePath, areaPath } from '~/utils/siteContent'

const route = useRoute()
const slug = computed(() => String(route.params.slug || ''))
const service = computed(() => getService(slug.value))

if (!service.value) {
  throw createError({ statusCode: 404, statusMessage: 'Service not found' })
}

const s = service.value

useSeoMeta({
  title: `${s.name} | ABC Painters`,
  description: `${s.description.slice(0, 150)} Serving Acworth, Kennesaw, and Cartersville, GA.`,
})

const crumbs = [
  { label: 'Home', to: '/' },
  { label: 'Services', to: '/services' },
  { label: s.name },
]

const siblings = SERVICES.filter((x) => x.slug !== s.slug)
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
          <img class="detail-hero" :src="s.image" :alt="s.heroDirection" width="1200" height="900" />
          <article class="content-card">
            <h2>About this service</h2>
            <p>{{ s.longDescription }}</p>
            <h3>What’s included</h3>
            <ul class="bullet-list">
              <li v-for="b in s.bullets" :key="b">{{ b }}</li>
            </ul>
            <h3>Cities we paint</h3>
            <p>
              <template v-for="(a, i) in SERVICE_AREAS" :key="a.slug">
                <NuxtLink :to="areaPath(a.slug)">{{ a.city }}</NuxtLink>
                <span v-if="i < SERVICE_AREAS.length - 1">, </span>
              </template>
            </p>
          </article>

          <div class="faq-block">
            <h2>{{ s.name }} FAQ</h2>
            <details v-for="(item, i) in s.faqs" :key="item.q" :open="i === 0">
              <summary>{{ item.q }}</summary>
              <p>{{ item.a }}</p>
            </details>
          </div>
        </div>

        <aside>
          <div class="silo-aside__card">
            <h2>Get an estimate</h2>
            <p class="muted">Tell us about your {{ s.name.toLowerCase() }} project.</p>
            <NuxtLink class="btn btn--primary" :to="`/contact?service=${s.service_key}`">Free estimate</NuxtLink>
            <NuxtLink class="btn btn--secondary" to="/portfolio">See portfolio</NuxtLink>
          </div>
          <div class="silo-aside__card">
            <h2>Other services</h2>
            <p v-for="x in siblings" :key="x.slug">
              <NuxtLink :to="servicePath(x.slug)">{{ x.name }}</NuxtLink>
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
  height: 18rem;
  object-fit: cover;
  border-radius: var(--radius-lg);
  margin-bottom: 1.25rem;
}

.faq-block {
  margin-top: 1.5rem;
  display: grid;
  gap: 0.65rem;
}

.faq-block h2 {
  margin-bottom: 0.35rem;
}

.faq-block details {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 0.85rem 1rem;
}

.faq-block summary {
  font-weight: 700;
  cursor: pointer;
}

.faq-block p {
  margin: 0.6rem 0 0.15rem;
}

aside {
  display: grid;
  gap: 1rem;
}
</style>
