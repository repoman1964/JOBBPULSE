<script setup lang="ts">
import { captionParts, instagramHandle } from '~/utils/socialPreview'

const props = defineProps<{
  companyName: string
  location?: string
  body: string
  imageUrl?: string | null
  compact?: boolean
}>()

const handle = computed(() => instagramHandle(props.companyName))
const parts = computed(() => captionParts(props.body))
</script>

<template>
  <article class="ig-post" :class="{ compact }">
    <header class="ig-head">
      <span class="ig-glyph" aria-hidden="true">
        <svg viewBox="0 0 24 24" width="18" height="18">
          <rect x="3" y="3" width="18" height="18" rx="5" fill="none" stroke="#fff" stroke-width="1.8" />
          <circle cx="12" cy="12" r="4.2" fill="none" stroke="#fff" stroke-width="1.8" />
          <circle cx="17.2" cy="6.8" r="1.1" fill="#fff" />
        </svg>
      </span>
      <div class="ig-id">
        <strong>{{ handle }}</strong>
        <span v-if="location">{{ location }}</span>
      </div>
      <span class="dots" aria-hidden="true">···</span>
    </header>

    <img
      v-if="imageUrl"
      class="ig-photo"
      :src="imageUrl"
      :alt="`${companyName} Instagram photo`"
    />
    <div v-else class="ig-photo ig-photo--empty" />

    <div class="ig-icons" aria-hidden="true">
      <span class="ig-icons-left">
        <svg viewBox="0 0 24 24" width="24" height="24">
          <path
            fill="none"
            stroke="#262626"
            stroke-width="1.8"
            d="M12.1 20.3s-7.4-4.5-9-8.4C1.6 8.4 3.7 5 7.2 5c2 0 3.3 1.1 4.9 2.8C13.7 6.1 15 5 17 5c3.5 0 5.6 3.4 4.1 6.9-1.6 3.9-9 8.4-9 8.4z"
          />
        </svg>
        <svg viewBox="0 0 24 24" width="24" height="24">
          <path
            fill="none"
            stroke="#262626"
            stroke-width="1.8"
            d="M21 11.5a8.4 8.4 0 0 1-12.6 7.3L4 20l1.4-4.1A8.4 8.4 0 1 1 21 11.5z"
          />
        </svg>
        <svg viewBox="0 0 24 24" width="24" height="24">
          <path fill="none" stroke="#262626" stroke-width="1.8" d="M4 4h16L12 13 4 4zm0 0v16l7.2-6.4" />
        </svg>
      </span>
      <svg viewBox="0 0 24 24" width="24" height="24">
        <path fill="none" stroke="#262626" stroke-width="1.8" d="M6 4h12v16l-6-4-6 4V4z" />
      </svg>
    </div>

    <p class="ig-caption">
      <strong>{{ handle }}</strong>
      <template v-for="(part, i) in parts" :key="i">
        <span v-if="part.type === 'tag'" class="tag">{{ part.value }}</span>
        <template v-else>{{ part.value }}</template>
      </template>
    </p>
  </article>
</template>

<style scoped>
.ig-post {
  background: #fff;
  color: #262626;
  border-radius: 12px;
  overflow: hidden;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
}

.ig-head {
  display: grid;
  grid-template-columns: 32px 1fr auto;
  gap: 10px;
  align-items: center;
  padding: 10px 12px;
}

.ig-glyph {
  width: 32px;
  height: 32px;
  border-radius: 9px;
  background: radial-gradient(circle at 30% 100%, #fccc63, #fbad50 20%, #e95950 45%, #d62976 70%, #962fbf);
  display: flex;
  align-items: center;
  justify-content: center;
}

.ig-id {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.ig-id strong {
  font-size: 0.85rem;
  font-weight: 700;
}

.ig-id span {
  font-size: 0.72rem;
  color: #8e8e8e;
}

.dots {
  color: #262626;
  font-weight: 700;
  letter-spacing: 1px;
}

.ig-photo {
  width: 100%;
  aspect-ratio: 1;
  object-fit: cover;
  background: #efefef;
}

.ig-photo--empty {
  min-height: 180px;
}

.ig-icons {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px 4px;
}

.ig-icons-left {
  display: flex;
  gap: 14px;
}

.ig-caption {
  margin: 0;
  padding: 4px 12px 12px;
  font-size: 0.88rem;
  line-height: 1.4;
}

.ig-caption strong {
  margin-right: 6px;
}

.tag {
  color: #00376b;
}

.compact .ig-caption {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.compact .ig-photo {
  aspect-ratio: 1;
}
</style>
