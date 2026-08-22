<script setup lang="ts">
export type SiloLink = {
  to: string
  title: string
  subtitle?: string
}

defineProps<{
  heading: string
  links: SiloLink[]
  /** compact = denser pill-style list for sidebars */
  variant?: 'cards' | 'pills'
}>()
</script>

<template>
  <section class="silo" :class="`silo--${variant || 'cards'}`" :aria-label="heading">
    <h2 class="silo__heading">{{ heading }}</h2>
    <ul class="silo__list">
      <li v-for="link in links" :key="link.to">
        <NuxtLink :to="link.to" class="silo__link">
          <span class="silo__title">{{ link.title }}</span>
          <span v-if="link.subtitle" class="silo__sub">{{ link.subtitle }}</span>
        </NuxtLink>
      </li>
    </ul>
  </section>
</template>

<style scoped>
.silo {
  margin-top: 2rem;
}

.silo__heading {
  font-size: 1.15rem;
  margin: 0 0 0.85rem;
}

.silo__list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: grid;
  gap: 0.65rem;
}

.silo--cards .silo__list {
  grid-template-columns: 1fr;
}

@media (min-width: 560px) {
  .silo--cards .silo__list {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (min-width: 900px) {
  .silo--cards .silo__list {
    grid-template-columns: repeat(3, 1fr);
  }
}

.silo--cards .silo__link {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  padding: 0.95rem 1rem;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  text-decoration: none !important;
  box-shadow: var(--shadow);
  height: 100%;
  transition: border-color 0.15s, transform 0.12s;
}

.silo--cards .silo__link:hover {
  border-color: var(--clay);
  transform: translateY(-1px);
}

.silo__title {
  font-weight: 700;
  color: var(--ink);
  font-size: 0.98rem;
}

.silo__sub {
  font-size: 0.85rem;
  color: var(--muted);
}

.silo--pills .silo__list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.45rem;
}

.silo--pills .silo__link {
  display: inline-flex;
  flex-direction: column;
  padding: 0.4rem 0.75rem;
  border-radius: var(--radius-pill);
  background: var(--clay-soft);
  border: 1px solid transparent;
  text-decoration: none !important;
}

.silo--pills .silo__link:hover {
  border-color: var(--clay);
}

.silo--pills .silo__title {
  font-size: 0.85rem;
  color: var(--clay-deep);
}

.silo--pills .silo__sub {
  display: none;
}
</style>
