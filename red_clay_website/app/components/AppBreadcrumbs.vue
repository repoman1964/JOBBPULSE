<script setup lang="ts">
export type Crumb = { label: string; to?: string }

defineProps<{
  items: Crumb[]
}>()
</script>

<template>
  <nav class="breadcrumbs" aria-label="Breadcrumb">
    <ol class="breadcrumbs__list">
      <li v-for="(item, i) in items" :key="`${item.label}-${i}`" class="breadcrumbs__item">
        <NuxtLink v-if="item.to && i < items.length - 1" :to="item.to" class="breadcrumbs__link">
          {{ item.label }}
        </NuxtLink>
        <span v-else class="breadcrumbs__current" aria-current="page">{{ item.label }}</span>
        <span v-if="i < items.length - 1" class="breadcrumbs__sep" aria-hidden="true">/</span>
      </li>
    </ol>
  </nav>
</template>

<style scoped>
.breadcrumbs {
  margin-bottom: 0.85rem;
}

.breadcrumbs__list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.35rem;
  font-size: 0.82rem;
  font-weight: 600;
}

.breadcrumbs__item {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
}

.breadcrumbs__link {
  color: var(--clay-dark);
  text-decoration: none !important;
}

.breadcrumbs__link:hover {
  text-decoration: underline !important;
}

.breadcrumbs__current {
  color: var(--muted);
}

.breadcrumbs__sep {
  color: #c4b5a8;
  font-weight: 500;
}
</style>
