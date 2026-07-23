<script setup lang="ts">
defineProps<{
  items: { slug: string; name: string; project_count?: number; public_path?: string }[]
}>()
</script>

<template>
  <div v-if="items?.length" class="chip-grid">
    <NuxtLink
      v-for="item in items"
      :key="item.slug"
      class="chip"
      :to="item.public_path || `/locations/${item.slug}`"
    >
      {{ item.name }}
      <span v-if="item.project_count != null" class="muted">&nbsp;({{ item.project_count }})</span>
    </NuxtLink>
  </div>
  <div v-else class="empty">No locations with published projects yet.</div>
</template>
