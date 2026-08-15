<script setup lang="ts">
import { cityOnly } from '~/utils/locationLabel'

defineProps<{
  items: { slug: string; name: string; city?: string; project_count?: number; public_path?: string }[]
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
      {{ cityOnly(item.city, item.name) }}
      <span v-if="item.project_count != null" class="muted">&nbsp;({{ item.project_count }})</span>
    </NuxtLink>
  </div>
  <div v-else class="empty">No locations with published projects yet.</div>
</template>
