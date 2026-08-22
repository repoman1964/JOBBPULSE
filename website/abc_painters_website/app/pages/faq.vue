<script setup lang="ts">
import { FAQS, SERVICES, servicePath } from '~/utils/siteContent'

useSeoMeta({
  title: 'FAQ | ABC Painters',
  description: 'Questions about estimates, prep, warranty, and service area for ABC Painters in Acworth, Georgia.',
})
</script>

<template>
  <div>
    <section class="page-hero">
      <div class="container">
        <AppBreadcrumbs :items="[{ label: 'Home', to: '/' }, { label: 'FAQ' }]" />
        <p class="section__eyebrow">FAQ</p>
        <h1 class="page-hero__title">Questions we hear most</h1>
        <p class="section__lead">
          Service-specific questions also live on
          <NuxtLink v-for="(s, i) in SERVICES" :key="s.slug" :to="servicePath(s.slug)">
            {{ s.name }}<span v-if="i < SERVICES.length - 1">, </span>
          </NuxtLink>.
        </p>
      </div>
    </section>

    <section class="section section--tight">
      <div class="container faq-list">
        <details v-for="(item, i) in FAQS" :key="item.q" :open="i === 0">
          <summary>{{ item.q }}</summary>
          <p>{{ item.a }}</p>
        </details>
      </div>
    </section>
  </div>
</template>

<style scoped>
.faq-list {
  display: grid;
  gap: 0.75rem;
  max-width: 46rem;
}

.faq-list details {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 0.9rem 1rem;
}

.faq-list summary {
  font-weight: 700;
  cursor: pointer;
}

.faq-list p {
  margin: 0.65rem 0 0.25rem;
}

.page-hero :deep(a) {
  color: #fff;
}
</style>
