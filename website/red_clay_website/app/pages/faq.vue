<script setup lang="ts">
import { FAQS } from '~/utils/siteContent'

useSeoMeta({
  title: 'FAQ | Red Clay Cabinet Installers',
  description: 'Common questions about cabinet installation timelines, service area, and estimates.',
})
</script>

<template>
  <div>
    <section class="page-hero">
      <div class="container">
        <p class="section__eyebrow">FAQ</p>
        <h1 class="page-hero__title">Questions we hear most</h1>
        <p class="section__lead">Don’t see yours? Call or send a note on the contact form.</p>
      </div>
    </section>

    <section class="section section--tight">
      <div class="container faq-list">
        <details v-for="(item, i) in FAQS" :key="item.q" class="faq" :open="i === 0">
          <summary>{{ item.q }}</summary>
          <p>{{ item.a }}</p>
        </details>
      </div>
    </section>
  </div>
</template>

<style scoped>
.page-hero {
  padding: 2.5rem 0 1rem;
  background: var(--clay-mist);
  border-bottom: 1px solid var(--border);
}

.page-hero__title {
  font-size: clamp(1.75rem, 3vw, 2.25rem);
}

.faq-list {
  display: grid;
  gap: 0.75rem;
  max-width: 46rem;
}

.faq {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 0.85rem 1rem;
  box-shadow: var(--shadow);
}

.faq summary {
  font-weight: 700;
  cursor: pointer;
  color: var(--ink);
}

.faq p {
  margin: 0.65rem 0 0.25rem;
}
</style>
