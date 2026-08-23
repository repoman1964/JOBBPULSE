<script setup lang="ts">
import { REVIEWS } from '~/utils/siteContent'

useSeoMeta({
  title: 'Reviews | Red Clay',
  description: 'On-site homeowner reviews for Red Clay painting across metro Atlanta.',
})
</script>

<template>
  <div>
    <section class="page-hero">
      <div class="container">
        <p class="section__eyebrow">Reviews</p>
        <h1 class="page-hero__title">What homeowners say</h1>
        <p class="section__lead">
          Words from houses we painted. Ask for a reference in your neighborhood.
        </p>
      </div>
    </section>

    <section class="section section--tight">
      <div class="container card-grid card-grid--2">
        <article v-for="r in REVIEWS" :key="r.author" class="review">
          <div class="review__stars" aria-label="5 stars">★★★★★</div>
          <p class="review__text">“{{ r.text }}”</p>
          <p class="review__by">
            <strong>{{ r.author }}</strong>
            <span class="muted"> · {{ r.location }}</span>
          </p>
        </article>
      </div>
      <div class="container" style="margin-top: 2rem; text-align: center">
        <NuxtLink class="btn btn--primary" to="/contact">Start your project</NuxtLink>
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

.review {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 1.25rem;
  box-shadow: var(--shadow);
}

.review__stars {
  color: #d97706;
  margin-bottom: 0.5rem;
}

.review__text {
  color: var(--ink);
  font-size: 1.02rem;
  margin: 0 0 0.85rem;
}

.review__by {
  margin: 0;
  font-size: 0.9rem;
}
</style>
