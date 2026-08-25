<script setup lang="ts">
const props = defineProps<{
  companyName: string
  location?: string
  body: string
  coverUrl?: string | null
  beforeUrl?: string | null
  afterUrl?: string | null
  compact?: boolean
}>()

const subline = computed(() => {
  const loc = props.location?.trim()
  return loc ? `Just now · ${loc}` : 'Just now'
})

const pair = computed(() => Boolean(props.beforeUrl && props.afterUrl && props.compact))
const hero = computed(() => props.coverUrl || props.afterUrl || props.beforeUrl || '')
</script>

<template>
  <article class="fb-post" :class="{ compact }">
    <header class="fb-head">
      <span class="fb-logo" aria-hidden="true">
        <svg viewBox="0 0 24 24" width="22" height="22">
          <path
            fill="#fff"
            d="M14.5 8.5V6.8c0-.7.5-1.3 1.5-1.3h1.2V3h-2.1C12.3 3 11 4.6 11 6.7v1.8H9v2.6h2V21h3.5v-9.9h2.3l.5-2.6h-2.8z"
          />
        </svg>
      </span>
      <div class="fb-id">
        <strong>{{ companyName }}</strong>
        <span>
          {{ subline }}
          <span class="globe" aria-hidden="true">🌐</span>
        </span>
      </div>
      <span class="dots" aria-hidden="true">···</span>
    </header>

    <p class="fb-caption">{{ body }}</p>

    <div v-if="pair" class="fb-pair">
      <img :src="beforeUrl!" alt="Before" />
      <img :src="afterUrl!" alt="After" />
    </div>
    <img v-else-if="hero" class="fb-hero" :src="hero" :alt="`${companyName} Facebook photo`" />

    <div class="fb-reactions" aria-hidden="true">
      <span class="rxn like">👍</span>
      <span class="rxn love">❤️</span>
    </div>
    <div class="fb-actions" aria-hidden="true">
      <span>Like</span>
      <span>Comment</span>
      <span>Share</span>
    </div>
  </article>
</template>

<style scoped>
.fb-post {
  background: #fff;
  color: #050505;
  border-radius: 12px;
  overflow: hidden;
  font-family: Helvetica, Arial, sans-serif;
  border: 1px solid #ced0d4;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.06);
}

.fb-head {
  display: grid;
  grid-template-columns: 40px 1fr auto;
  gap: 10px;
  align-items: center;
  padding: 12px 12px 8px;
}

.fb-logo {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: #1877f2;
  display: flex;
  align-items: center;
  justify-content: center;
}

.fb-id {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.fb-id strong {
  font-size: 0.92rem;
  font-weight: 700;
  line-height: 1.2;
}

.fb-id span {
  font-size: 0.75rem;
  color: #65676b;
}

.globe {
  font-size: 0.7rem;
}

.dots {
  color: #65676b;
  letter-spacing: 1px;
  font-weight: 700;
}

.fb-caption {
  margin: 0;
  padding: 0 12px 10px;
  font-size: 0.95rem;
  line-height: 1.4;
  color: #050505;
}

.compact .fb-caption {
  display: -webkit-box;
  -webkit-line-clamp: 4;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.fb-hero {
  width: 100%;
  aspect-ratio: 4 / 3;
  object-fit: cover;
  background: #e4e6eb;
}

.fb-pair {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2px;
  background: #fff;
}

.fb-pair img {
  width: 100%;
  aspect-ratio: 1;
  object-fit: cover;
  background: #e4e6eb;
}

.fb-reactions {
  display: flex;
  align-items: center;
  padding: 8px 12px;
  font-size: 0.85rem;
}

.rxn {
  width: 18px;
  height: 18px;
  border-radius: 50%;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 0.7rem;
  margin-right: -4px;
}

.fb-actions {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  border-top: 1px solid #ced0d4;
  color: #65676b;
  font-size: 0.82rem;
  font-weight: 600;
  text-align: center;
}

.fb-actions span {
  padding: 10px 0;
}

.compact .fb-head {
  padding: 10px 10px 6px;
}

.compact .fb-caption {
  padding: 0 10px 8px;
  font-size: 0.85rem;
}

.compact .fb-hero {
  aspect-ratio: 16 / 10;
}

.compact .fb-actions span {
  padding: 8px 0;
  font-size: 0.75rem;
}
</style>
