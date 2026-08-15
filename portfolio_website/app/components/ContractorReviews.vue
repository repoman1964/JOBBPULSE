<script setup lang="ts">
import type { DemoReview } from '~/utils/contractorDemo'

defineProps<{
  reviews: DemoReview[]
  rating?: number
  reviewCount?: number
}>()
</script>

<template>
  <section v-if="reviews?.length" class="contractor-reviews">
    <div class="contractor-reviews__header">
      <h2 class="section__title" style="margin: 0">Google Reviews</h2>
      <span v-if="rating != null" class="contractor-reviews__summary">
        <span class="contractor-reviews__stars" aria-hidden="true">★</span>
        {{ rating.toFixed(1) }}
        <span v-if="reviewCount" class="muted">({{ reviewCount }} reviews)</span>
      </span>
    </div>
    <div class="contractor-reviews__track">
      <article v-for="(r, i) in reviews" :key="i" class="review-card">
        <div class="review-card__top">
          <span class="review-card__avatar" aria-hidden="true">{{ r.author.charAt(0) }}</span>
          <div>
            <div class="review-card__author">{{ r.author }}</div>
            <div class="review-card__meta">
              <span class="review-card__stars" :aria-label="`${r.rating} stars`">
                {{ '★'.repeat(Math.round(r.rating)) }}
              </span>
              <span class="muted">{{ r.date }}</span>
            </div>
          </div>
        </div>
        <p class="review-card__text">{{ r.text }}</p>
      </article>
    </div>
  </section>
</template>

<style scoped>
.contractor-reviews {
  margin: 1.75rem 0;
}

.contractor-reviews__header {
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  justify-content: space-between;
  gap: 0.5rem 1rem;
  margin-bottom: 0.95rem;
}

.contractor-reviews__summary {
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--text);
}

.contractor-reviews__stars {
  color: #f59e0b;
  margin-right: 0.15rem;
}

.contractor-reviews__track {
  display: grid;
  gap: 0.75rem;
  grid-template-columns: 1fr;
}

@media (min-width: 640px) {
  .contractor-reviews__track {
    grid-template-columns: repeat(3, 1fr);
  }
}

.review-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 0.9rem 1rem;
  box-shadow: var(--shadow);
}

.review-card__top {
  display: flex;
  gap: 0.65rem;
  align-items: flex-start;
  margin-bottom: 0.55rem;
}

.review-card__avatar {
  width: 2rem;
  height: 2rem;
  border-radius: 50%;
  background: #4285f4;
  color: #fff;
  display: grid;
  place-items: center;
  font-size: 0.85rem;
  font-weight: 700;
  flex-shrink: 0;
}

.review-card__author {
  font-weight: 650;
  font-size: 0.9rem;
  line-height: 1.2;
}

.review-card__meta {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem 0.5rem;
  font-size: 0.78rem;
  margin-top: 0.15rem;
}

.review-card__stars {
  color: #f59e0b;
  letter-spacing: 0.02em;
}

.review-card__text {
  margin: 0;
  font-size: 0.88rem;
  color: var(--muted);
  line-height: 1.45;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
