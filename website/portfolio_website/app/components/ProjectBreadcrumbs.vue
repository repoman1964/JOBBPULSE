<script setup lang="ts">
defineProps<{
  items: { label: string; to?: string }[]
}>()
</script>

<template>
  <nav class="breadcrumbs" aria-label="Breadcrumb">
    <template v-for="(item, index) in items" :key="`${item.label}-${index}`">
      <span v-if="index > 0">/</span>
      <NuxtLink v-if="item.to" :to="item.to">{{ item.label }}</NuxtLink>
      <span v-else>{{ item.label }}</span>
    </template>
  </nav>
</template>
