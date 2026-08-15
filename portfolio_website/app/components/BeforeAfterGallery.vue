<script setup lang="ts">
import type { MediaItem } from '~/composables/usePublicApi'

const props = defineProps<{
  media: MediaItem[]
}>()

const groups = computed(() => {
  const order = ['before', 'during', 'after', 'additional']
  const map = new Map<string, MediaItem[]>()
  for (const item of props.media || []) {
    if (!item?.url) continue
    const stage = (item.stage_label || 'additional').toLowerCase()
    if (!map.has(stage)) map.set(stage, [])
    map.get(stage)!.push(item)
  }
  return order
    .filter((key) => map.has(key))
    .map((key) => ({
      key,
      label: key.charAt(0).toUpperCase() + key.slice(1),
      items: (map.get(key) || []).sort((a, b) => a.display_order - b.display_order),
    }))
})
</script>

<template>
  <div v-if="groups.length" class="gallery">
    <div v-for="group in groups" :key="group.key" class="gallery__group">
      <h3>{{ group.label }}</h3>
      <div class="gallery__row">
        <a
          v-for="item in group.items"
          :key="item.id"
          :href="item.url || undefined"
          target="_blank"
          rel="noopener"
        >
          <img :src="item.url!" :alt="`${group.label} photo`" loading="lazy" />
        </a>
      </div>
    </div>
  </div>
  <div v-else class="empty">Photos will appear here when available.</div>
</template>
