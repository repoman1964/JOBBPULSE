<script setup lang="ts">
import { companyInitials } from '~/utils/socialPreview'

const props = defineProps<{
  companyName: string
  location?: string
  body: string
  imageUrl?: string | null
  compact?: boolean
}>()

const initials = computed(() => companyInitials(props.companyName))
const subline = computed(() => {
  const loc = props.location?.trim()
  return loc ? `Google · ${loc}` : 'Google Business Profile'
})
</script>

<template>
  <article class="gbp-post" :class="{ compact }">
    <header class="gbp-head">
      <span class="gbp-avatar" aria-hidden="true">{{ initials }}</span>
      <div class="gbp-id">
        <strong>{{ companyName }}</strong>
        <span>{{ subline }}</span>
      </div>
      <span class="gbp-mark" aria-hidden="true">
        <svg viewBox="0 0 24 24" width="18" height="18">
          <path fill="#4285F4" d="M21.6 12.23c0-.74-.07-1.45-.19-2.13H12v4.03h5.38a4.6 4.6 0 0 1-2 3.02v2.5h3.23c1.89-1.74 2.99-4.31 2.99-7.42z" />
          <path fill="#34A853" d="M12 22c2.7 0 4.96-.9 6.61-2.35l-3.23-2.5c-.9.6-2.04.96-3.38.96-2.6 0-4.8-1.76-5.58-4.12H3.09v2.58A10 10 0 0 0 12 22z" />
          <path fill="#FBBC05" d="M6.42 13.99A6.01 6.01 0 0 1 6.1 12c0-.69.12-1.36.32-1.99V7.43H3.09A10 10 0 0 0 2 12c0 1.61.39 3.14 1.09 4.57l3.33-2.58z" />
          <path fill="#EA4335" d="M12 5.87c1.47 0 2.79.5 3.83 1.5l2.87-2.87C16.95 2.9 14.7 2 12 2A10 10 0 0 0 3.09 7.43l3.33 2.58C7.2 7.63 9.4 5.87 12 5.87z" />
        </svg>
      </span>
    </header>

    <img
      v-if="imageUrl"
      class="gbp-photo"
      :src="imageUrl"
      :alt="`${companyName} Google Business photo`"
    />
    <div v-else class="gbp-photo gbp-photo--empty" />

    <p class="gbp-caption">{{ body }}</p>

    <div class="gbp-cta" aria-hidden="true">
      <span>Call</span>
      <span>Learn more</span>
    </div>
  </article>
</template>

<style scoped>
.gbp-post {
  background: #fff;
  color: #202124;
  border-radius: 12px;
  overflow: hidden;
  font-family: 'Google Sans', Roboto, Helvetica, Arial, sans-serif;
  border: 1px solid #e8eaed;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.06);
}

.gbp-head {
  display: grid;
  grid-template-columns: 40px 1fr auto;
  gap: 10px;
  align-items: center;
  padding: 12px 12px 8px;
}

.gbp-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: #1a73e8;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.78rem;
  font-weight: 700;
}

.gbp-id {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.gbp-id strong {
  font-size: 0.92rem;
  font-weight: 700;
  line-height: 1.2;
}

.gbp-id span {
  font-size: 0.75rem;
  color: #5f6368;
}

.gbp-mark {
  display: flex;
  align-items: center;
}

.gbp-photo {
  width: 100%;
  aspect-ratio: 16 / 10;
  object-fit: cover;
  background: #e8eaed;
}

.gbp-photo--empty {
  min-height: 140px;
}

.gbp-caption {
  margin: 0;
  padding: 10px 12px 8px;
  font-size: 0.92rem;
  line-height: 1.45;
  color: #202124;
}

.compact .gbp-caption {
  display: -webkit-box;
  -webkit-line-clamp: 4;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.gbp-cta {
  display: grid;
  grid-template-columns: 1fr 1fr;
  border-top: 1px solid #e8eaed;
  color: #1a73e8;
  font-size: 0.82rem;
  font-weight: 600;
  text-align: center;
}

.gbp-cta span {
  padding: 10px 0;
}

.gbp-cta span + span {
  border-left: 1px solid #e8eaed;
}

.compact .gbp-head {
  padding: 10px 10px 6px;
}

.compact .gbp-caption {
  padding: 8px 10px 6px;
  font-size: 0.85rem;
}

.compact .gbp-cta span {
  padding: 8px 0;
  font-size: 0.75rem;
}
</style>
